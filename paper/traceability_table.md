| # | project | HEAD | commits | single-key | multi-key | verdict | drop reason (measured) |
|---|---|---|---:|---:|---:|---|---|
| 1 | hive | `6730aadd18` | 18,213 | 97.0% | **97.0%** | pass | — |
| 2 | phoenix | `1b55fb4b33` | 4,264 | 92.0% | **92.0%** | pass | — |
| 3 | oozie | `8bdac8be4f` | 2,412 | 85.2% | **85.2%** | pass | — |
| 4 | knox | `6bdf64cdfd` | 3,194 | 84.4% | **84.4%** | pass | — |
| 5 | drill | `86e9b82f16` | 4,594 | 84.2% | **84.2%** | pass | — |
| 6 | kylin | `b5b94b51ab` | 968 | 83.9% | **83.9%** | pass | — |
| 7 | atlas | `b45faecc96` | 4,140 | 78.1% | **78.1%** | drop | below_bar_narrowly |
| 8 | flume | `9acf154361` | 2,084 | 73.9% | **73.9%** | drop | below_bar_narrowly |
| 9 | calcite | `8447eda2f2` | 6,746 | 66.4% | **67.7%** | drop | low_commit_message_hygiene |
| 10 | accumulo | `5c7d96deb6` | 15,069 | 43.0% | **43.0%** | drop | low_commit_message_hygiene |
| 11 | parquet-java | `83c2c80d49` | 2,990 | 29.1% | **29.1%** | drop | github_issue_references_dominate |
| 12 | helix | `0902505fda` | 4,926 | 10.4% | **10.4%** | drop | github_issue_references_dominate |

**6 of 12 pass the 0.80 bar.**
