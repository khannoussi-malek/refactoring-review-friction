#!/usr/bin/env python3
"""
jira_archive.py — stream a gzip-wrapped mongodump archive without restoring it.

The Public Jira Dataset (Zenodo 15719919) ships as
`mongodump --db=JiraReposAnon --gzip --archive=...`. The published restore path
needs mongorestore, a running mongod, and ~60 GB expanded. This reads the
archive as a stream instead: nothing is restored, nothing is extracted, and the
5.87 GB body is decompressed on the fly straight out of the enclosing zip.

ARCHIVE FORMAT (mongodb/mongo-tools `archive` package)

    Archive          := Magic ArchiveHeader *Namespace EOF
    Magic            := int32 0x8199e26d
    ArchiveHeader    := BSON
    Namespace        := NamespaceHeader *BSON Terminator
    NamespaceHeader  := BSON {db, collection, EOF, CRC}
    Terminator       := int32 0xFFFFFFFF

`--gzip` wraps the WHOLE stream, so the file begins with 1f8b (gzip) and the
archive magic appears only after decompression.

Discriminating headers from data: a namespace header or a collection-metadata
doc carries `db` and `collection` and never carries `_id`; every issue document
carries `_id`. That test is exact here and avoids depending on key order.

Usage:
    python3 scripts/jira_archive.py --zip <dataset.zip> --stage validate
    python3 scripts/jira_archive.py --stage ... (see jira_estimates.py)
"""
import gzip, struct, zipfile

import bson

MAGIC = 0x8199E26D
TERMINATOR = 0xFFFFFFFF
MEMBER = "ThePublicJiraDataset/3. DataDump/mongodump-JiraReposAnon.archive"


def _read_exact(fh, n):
    """GzipFile.read may short-read; BSON framing cannot tolerate that."""
    buf = b""
    while len(buf) < n:
        chunk = fh.read(n - len(buf))
        if not chunk:
            return buf
        buf += chunk
    return buf


def stream_archive(zip_path, member=MEMBER, on_namespace=None):
    """Yield (db, collection, document) for every document in the archive.

    on_namespace: optional callback fired when a data block for a namespace
    starts, so callers can log progress without inspecting documents.
    """
    zf = zipfile.ZipFile(zip_path)
    with zf.open(member) as raw, gzip.GzipFile(fileobj=raw, mode="rb") as fh:
        magic = struct.unpack("<I", _read_exact(fh, 4))[0]
        if magic != MAGIC:
            raise SystemExit(f"not a mongodump archive: magic {magic:#x}")

        ns = (None, None)
        first = True
        while True:
            head = _read_exact(fh, 4)
            if len(head) < 4:
                return                                  # clean end of stream
            (val,) = struct.unpack("<I", head)
            if val == TERMINATOR:
                ns = (None, None)                       # end of a data block
                continue
            body = _read_exact(fh, val - 4)
            if len(body) < val - 4:
                return                                  # truncated tail
            doc = bson.decode(head + body)

            if first:                                   # archive header
                first = False
                continue
            if "_id" not in doc and "db" in doc and "collection" in doc:
                ns = (doc["db"], doc["collection"])      # header or metadata
                if on_namespace and not doc.get("metadata"):
                    on_namespace(ns[0], ns[1])
                continue
            yield ns[0], ns[1], doc
