# F2 codebook labeling set (40 real hadoop review comments)

Label each comment per `codebook.md`:
- **S** = STRUCTURAL (argues about code shape: extract/move/split/interface/coupling/where-it-lives)
- **I** = INCIDENTAL (structural word present, but not an argument — fact, trivial edit, different meaning)
- **C** = STYLE/CORRECTNESS (real review, but about behaviour/tests/naming/approval)

Two raters fill A and B independently, then compute Cohen's κ. Rows 1-20 tripped the keyword filter; 21-40 did not.

| # | Ticket | Comment | A | B |
|---|--------|---------|---|---|
| 1 | YARN-10189 | HI [~bteke], Good job, very nice refactor. Latest patch LGTM, committed to trunk. Please take care of uploading patches for branch-3.3 and branch-3.2 to have a jenkins result for both branches. Thanks |   |   |
| 2 | HDFS-15346 | Hi [~LiJinglun], HDFS-15340 is merged now. I suggest you can split remaining work to two subtasks: * One for DistCpFedBalance implement (we will do this on current JIRA) * Document of fedbalance tool (need to create a new JIRA) |   |   |
| 3 | HDFS-16174 | Thanks [~gautham] for the refactor. Merged PR 3303 to trunk. |   |   |
| 4 | HADOOP-18073 | Thanks [~mthakur] , I've run the test and all ok. For the refactoring of that method, i'd prefer to do it as a separate PR. If all looks good to you, could you/[~stevel@apache.org] please push this rebased branch up to the feature branch? |   |   |
| 5 | HADOOP-14445 | [~weichiu]: Thanks a lot for your test case from HADOOP-14441. I just added couple of things like renew and cancel token in addition to your test case. |   |   |
| 6 | HDDS-1717 | I have tried resolving this without duplicating the classes. I have refactored OMProxyInfo to not extend FailoverProxyProvider.ProxyInfo. |   |   |
| 7 | HDFS-14854 | I spotted a couple of minor issues with the v5 patch so I have uploaded v6. |   |   |
| 8 | HDFS-14997 | +1 on [^HDFS-14997.005.patch]. This is pretty core, so I'll give it a couple days before committing in case somebody else has comments. |   |   |
| 9 | HADOOP-14178 | The upgrade will be very big change, so I'd like to split this into some sub-tasks to reduce the cost of review. The first sub-task is to remove the usage of Whitebox, which was removed in Mockito 2.1. I'll add sub-tasks later if needed. |   |   |
| 10 | HADOOP-14178 | bq. The patch becomes bigger and bigger. I'd like to split the patch for each modules for reviewers to review the patches easily. This is not simple. Mockito 1.x and 2.x use the same package name, so we need to exclude the dependency appropriately and this it is very hard work. |   |   |
| 11 | HADOOP-16125 | [^HADOOP-16125.003.patch] looks clean as clean can be. +1 I'll wait a couple days for committing in case anybody has comments. |   |   |
| 12 | HDDS-1458 | bq. The disk tests are only setting up structure to run inline in maven only. Can we support both the approaches? |   |   |
| 13 | HDFS-13215 | It looks like people is mostly positive about this change. I'd go ahead but I don't have much cycles this week so I'd appreciate if anybody can do the refactor. Anybody willing to take this? |   |   |
| 14 | HDFS-13033 | {quote} # moveBlock logic seems to be duplicated. Can we refactor to keep common?{quote} I've created {{StoragePolicySatisfyUtils}} class to keep commonly used functions. Attached another patch addressing all the above Uma's comments. Please review, thanks! |   |   |
| 15 | HDFS-13790 | This is mostly refactoring of {{RouterRpcServer}}, if anybody is interested please feel free to assign this JIRA to you. If nobody volunteers, I can take it over eventually. |   |   |
| 16 | YARN-7988 | Attached v1 patch for refactoring . [~Naganarasimha]/[~cheersyang]/[~sunilg] could you please review |   |   |
| 17 | HDFS-11106 | +1 on 001.patch. The refactoring is definitely helpful for future development. |   |   |
| 18 | HDFS-11920 | [~vagarychen] Thanks for taking care of this. I think it would be a good idea to support a seek interface or FileChannel interface in the new group streams. |   |   |
| 19 | HDDS-18 | [~nandakumar131] Thanks for reviewing the patch! HDDS-18.001.patch addresses your comments. In OzoneClientFactory now I am just logging the error message. Also I have refactored OzoneRestClientException to OzoneClientException. |   |   |
| 20 | HADOOP-18679 | update, #5081 does successfully show the staging UT failure (good!) but also some in hadoop-common due to the new interface...we need to modify the tests to indicate it is safe to not override the base implementation. |   |   |
| 21 | YARN-10189 | Uploaded a solution proposal as PoC patch. It's up for discussion. |   |   |
| 22 | HDFS-15973 | Let's fix the whitespace warning and while we are at it, in the documentation let's use RPC in capitals. BTW, is just removing the sleep good enough? There is no need to wait for anything? We went very fast from 100 to 0. |   |   |
| 23 | HADOOP-18207 | I deleted 3.4.0 from the fix version. When PR is merged, we will set the fix version again. |   |   |
| 24 | HADOOP-18830 | going to cut this. it doesn't get used as predicate pushdown into the FS just confuses everything above it |   |   |
| 25 | YARN-10548 | [~gandras] Seems like none of the above failures are strongly related to my patch as I've been just moving around code. |   |   |
| 26 | HADOOP-14445 | I'll make an effort to review today but schedule is very hectic. My last proposal was centered around _not_ having another conf option so I'm not pleased that one was added. Initially I'm inclined to do something similar to Rushabh's last patch but I need to do a brain reload. |   |   |
| 27 | HDFS-14625 | Thanks [~hemanthboyina]! Pushed 004 patch to trunk. I'm not sure if this should go into lower branches. Please let me know. |   |   |
| 28 | HDFS-14997 | Linking an issue where the change in how we do command processing uncovers an old, existing problem. Perhaps it is of interest. |   |   |
| 29 | HDDS-748 | Thanks [~anu] the feedback. Removed the proposal tag. I also added a link: I think it blocks HDDS-763 (that would be more easy with separated codecs. |   |   |
| 30 | HDDS-805 | Patch v5 to fix failure in \{{TestSecureOzoneContainer}}. Others look unrelated. |   |   |
| 31 | YARN-9322 | Thanks! This is a good idea, will file the follow-up jira tomorrow. |   |   |
| 32 | HADOOP-16059 | [~elgoiri] Client to datanode connection will get fast for any operation that shall require the same |   |   |
| 33 | HDFS-14508 | Oh, I thought HDFS-14475 was already in. [~crh] can you take a look at [^HDFS-14508-HDFS-13891.2.patch]? The new approach seems reasonable to me. I remember there was some kind of documentation for the metrics too. |   |   |
| 34 | HDFS-11695 | Thanks [~umamaheswararao] for review... Attached updated patch, Pls review.. |   |   |
| 35 | HDDS-265 | [~ljain], [~hanishakoneru] Thanks for reviewing and committing this. |   |   |
| 36 | HADOOP-15663 | Updated fixed version to 3.2.0 as HADOOP-15407 branch is merged to trunk |   |   |
| 37 | HDFS-13328 | FYI, attached [^HDFS-13328-05.patch], where I made a very small change. Just removed one new line in {{ReencryptionHandler.java}} class in order to make cherry pick smooth. |   |   |
| 38 | HDFS-11775 | Thanks [~nandakumar131] for the contribution and all for the reviews. I've commit the patch to the feature branch. |   |   |
| 39 | HDFS-12387 | Thanks for the update. +1 given the test issue is understood. |   |   |
| 40 | HADOOP-19047 | @steveloughran - I am glad to assist with the testing. Is there any release candidate branch for the same? Could you please share the wiki on what tests needs to be done? |   |   |
