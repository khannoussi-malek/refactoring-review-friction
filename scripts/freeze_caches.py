#!/usr/bin/env python3
"""
freeze_caches.py — package the Jira API caches for deposit.

paper/REPRODUCIBILITY.md identified these five directories as the single most
serious reproducibility gap in the repo: they are gitignored, they are the input
to every statistical result in the dossier, and nothing rebuilds them. They also
cannot be rebuilt faithfully even in principle — Jira is live, tickets keep
changing, and a 2026 re-fetch would not return the 2026-07 state these results
were computed from.

So they get deposited, not regenerated. This produces a versioned archive plus a
manifest recording, per file: SHA-256, byte size, and modification time; and per
directory: file count, total bytes, and the date range of the API pulls.

This deliberately does NOT write a rebuild script. A rebuild script would imply
the caches are reproducible from the API, and they are not.

Usage:
    python3 scripts/freeze_caches.py --version v1 --out deposit/
"""
import argparse, datetime as dt, hashlib, json, os, tarfile

CACHES = [".jira_cache", ".jira_changelog", ".jira_props", ".jira_assignee", ".jira_control"]
JIRA_BASE = "https://issues.apache.org/jira"


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(buf), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root):
    """Per-file digest + size + mtime, and the directory's pull date range."""
    files, total, mtimes = {}, 0, []
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if not os.path.isfile(p):
            continue
        st = os.stat(p)
        files[name] = {
            "sha256": sha256(p),
            "bytes": st.st_size,
            "mtime_utc": dt.datetime.utcfromtimestamp(st.st_mtime).isoformat() + "Z",
        }
        total += st.st_size
        mtimes.append(st.st_mtime)
    return {
        "file_count": len(files),
        "total_bytes": total,
        "pull_range_utc": {
            "first": dt.datetime.utcfromtimestamp(min(mtimes)).isoformat() + "Z" if mtimes else None,
            "last": dt.datetime.utcfromtimestamp(max(mtimes)).isoformat() + "Z" if mtimes else None,
        },
        "files": files,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    ap.add_argument("--out", default="deposit")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    missing = [d for d in CACHES if not os.path.isdir(d)]
    if missing:
        raise SystemExit(f"missing cache directories: {missing}")

    print("Inventorying (SHA-256 per file)...")
    dirs = {d: inventory(d) for d in CACHES}
    for d, v in dirs.items():
        print(f"  {d:18s} {v['file_count']:5d} files  {v['total_bytes']/1e6:7.2f} MB  "
              f"{v['pull_range_utc']['first'][:10]} .. {v['pull_range_utc']['last'][:10]}")

    all_m = [f["mtime_utc"] for v in dirs.values() for f in v["files"].values()]
    manifest = {
        "archive_version": args.version,
        "created_utc": dt.datetime.utcnow().isoformat() + "Z",
        "source": JIRA_BASE,
        "api": "Jira REST API v2",
        "description": (
            "Jira API response caches for the Apache Hadoop architectural-refactoring "
            "study. Five directories: raw issues (.jira_cache), status changelogs "
            "(.jira_changelog), issue properties (.jira_props), assignee/reporter "
            "(.jira_assignee), and the ordinary-refactoring control group "
            "(.jira_control). These are point-in-time snapshots; Jira is live and a "
            "re-fetch will not reproduce them."
        ),
        "totals": {
            "file_count": sum(v["file_count"] for v in dirs.values()),
            "total_bytes": sum(v["total_bytes"] for v in dirs.values()),
        },
        "pull_range_utc": {"first": min(all_m), "last": max(all_m)},
        "directories": dirs,
    }

    tar_path = os.path.join(args.out, f"jira-caches-{args.version}.tar.gz")
    print(f"\nWriting {tar_path} ...")
    with tarfile.open(tar_path, "w:gz") as tf:
        for d in CACHES:
            tf.add(d, arcname=d)
    manifest["archive"] = {
        "name": os.path.basename(tar_path),
        "bytes": os.path.getsize(tar_path),
        "sha256": sha256(tar_path),
    }

    mpath = os.path.join(args.out, f"MANIFEST-{args.version}.json")
    json.dump(manifest, open(mpath, "w"), indent=1)

    # Human-readable summary, without the per-file digests.
    lines = [
        f"# Jira cache archive — {args.version}", "",
        f"- **Archive**: `{manifest['archive']['name']}` "
        f"({manifest['archive']['bytes']/1e6:.2f} MB)",
        f"- **SHA-256**: `{manifest['archive']['sha256']}`",
        f"- **Files**: {manifest['totals']['file_count']:,} "
        f"({manifest['totals']['total_bytes']/1e6:.2f} MB uncompressed)",
        f"- **Source**: {JIRA_BASE} (Jira REST API v2)",
        f"- **API pulls**: {manifest['pull_range_utc']['first'][:19]}Z "
        f"→ {manifest['pull_range_utc']['last'][:19]}Z",
        f"- **Created**: {manifest['created_utc'][:19]}Z", "",
        "| directory | files | MB | first pull | last pull |",
        "|---|---:|---:|---|---|",
    ]
    for d, v in dirs.items():
        lines.append(f"| `{d}` | {v['file_count']:,} | {v['total_bytes']/1e6:.2f} | "
                     f"{v['pull_range_utc']['first'][:19]}Z | {v['pull_range_utc']['last'][:19]}Z |")
    lines += ["",
              "Per-file SHA-256 digests are in the JSON manifest alongside this file.", "",
              "**These caches are not regenerable.** Jira is live: issues are edited, "
              "reopened and occasionally deleted, so a re-fetch returns a different "
              "state. Every statistical result in `results_dossier.md` is computed "
              "from this snapshot, which is why it is deposited rather than scripted."]
    open(os.path.join(args.out, f"MANIFEST-{args.version}.md"), "w").write("\n".join(lines) + "\n")

    print(f"  archive {manifest['archive']['bytes']/1e6:.2f} MB")
    print(f"  sha256  {manifest['archive']['sha256']}")
    print(f"Wrote {mpath} and MANIFEST-{args.version}.md")


if __name__ == "__main__":
    main()
