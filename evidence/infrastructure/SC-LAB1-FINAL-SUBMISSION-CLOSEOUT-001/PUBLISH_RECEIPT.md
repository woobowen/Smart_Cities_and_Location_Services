# 实验一最终收尾：发布回执

任务：SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001。Engineering PASS；网页最终二审 PENDING，Deliverable FINAL_REVIEW，Submission NOT_READY，sent_to_teacher=false，Understanding LEARNING。本轮未发送邮件或操作教学平台。

## 内容提交与发布

- 起始/上轮已审基线：`9d91392289b31a4afa5c94cfd3869da9f021b4ad`。
- 本轮被审工程内容提交：`543e2c5deec7dc9d75598c7e1096b334a11a6fab`，分支 `main`，正常 `git push origin main` 退出0。原始命令与输出见 [content_publish_command.json](content_publish_command.json)。
- 该提交包含新Process原件/397成员源、最小入口与打包维护、正式教师目录及ZIP、真实构建/终检、独立内部审查。
- 本回执和远程检查记录在后续独立回执提交发布；最终HEAD在CLI最终返回并再次从直接远程及FETCH_HEAD核对，不在本文件写自身提交SHA。
- 后续提交须仅追加/承接本任务发布核验记录，工程成品及代码保持上述内容提交原字节。最终差异范围和实际回读由仓库外最终核验记录保存，避免SHA自引用。

## 真实远程回读

核验时间：`2026-10-03T02:41:53.689185+00:00`。从仓库外全新bare对象库网络fetch，验证准确origin/bare、清除Git对象环境覆盖变量，fetch前后确认无alternates；真实记录见 [remote_content_verification.json](remote_content_verification.json)，命令退出0见 [remote_content_command.json](remote_content_command.json)。

| 实际位置 | SHA |
|---|---|
| Local HEAD | `543e2c5deec7dc9d75598c7e1096b334a11a6fab` |
| origin/main | `543e2c5deec7dc9d75598c7e1096b334a11a6fab` |
| 直接远程 main | `543e2c5deec7dc9d75598c7e1096b334a11a6fab` |
| 独立 FETCH_HEAD | `543e2c5deec7dc9d75598c7e1096b334a11a6fab` |

以`git show FETCH_HEAD:path`读回550个实际文件；全部与本地已审字节相等。核对15项批准project sources完整集合、每项active/release字节及新输入hash；工作源397成员逐文件同输入ZIP；正式教师ZIP真实下载后CRC通过，manifest与Git文件夹的116个成员精确同字节。复用对象库再次fetch须继续解析FETCH_HEAD，不依赖浅克隆本地branch快进。

独立审查随后另行使用`git cat-file --batch`实际读出551个blob，重算Git对象SHA1和文件SHA256：其中550项逐一确认上述全部产物，另1项核对已冻结辅助脚本。实际查询remote HEAD、源ZIP397成员、正式教师ZIP与116个远程目录成员均PASS，见 [independent_remote_publication_check.json](independent_remote_publication_check.json) 与 [INTERNAL_REVIEW §7](INTERNAL_REVIEW.md#7-已发布内容的独立实际对象回读)。网络fetch为主线程执行，独立新增范围为自己的对象读取和产物复核。

## 固定成品

| 成品 | 字节数 | SHA256 |
|---|---:|---|
| Process PDF | 8143247 | `dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23` |
| Process源ZIP | 56878339 | `831d61baa7de160796827b60f29e1ada9f1b3809c2a87aa4acd6b98703e352ef` |
| 正式教师候选ZIP | 23599893 | `c1d0b80313f81e81a6bcd4cc02d06002c442201379ea871c4c338386bde2eb66` |

教师文件夹：`task1/submission/teacher-delivery/10245102410_吴博闻_实验一/`。115个manifest声明文件+manifest自身=116个普通文件；ZIP在目录外，目录与ZIP每文件集合/字节一致。两PDF25/77页、两个完成版Notebook代码与原件字节保持；本轮完成fresh解压CLI/probe，未Run All、模型调用0、轨迹处理0。

## 网页最终二审入口

- [REVIEW_PACKET](REVIEW_PACKET.md)、[INTERNAL_REVIEW](INTERNAL_REVIEW.md)、[真实教师ZIP终检](teacher_zip_final_check.json)、[独立实包隔离检查](independent_teacher_fresh_validation.json)。
- 内容提交固定路径：[正式教师ZIP](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/543e2c5deec7dc9d75598c7e1096b334a11a6fab/task1/submission/teacher-delivery/10245102410_吴博闻_实验一.zip)、[新Process PDF](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/543e2c5deec7dc9d75598c7e1096b334a11a6fab/reports/process-report/experiment1-revised/Process_Report_Revised.pdf)、[新Process源ZIP](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/543e2c5deec7dc9d75598c7e1096b334a11a6fab/reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip)、[唯一来源清单](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/543e2c5deec7dc9d75598c7e1096b334a11a6fab/evidence/infrastructure/chatgpt-project-source-sync/sources.json)。
- 上轮网页PASS仅继承9d91392的原审核；本轮内部PASS与远程回读不冒称网页最终二审或新逐页用户验收。新PDF按既有全文验收+用户授权p76修正承接；没有历史Evidence Lock补签。
- Project Sources仅两项变化，其余13项保持；UI新两项上传尚无本轮用户报告，USER_CONFIRMATION_REQUIRED，Project Settings未改。
- 教师PPT第26页要求10月5日前发送至52285903012@stu.ecnu.edu.cn，未给具体钟点。通过最后二审与用户确认后，由用户发送正式命名ZIP；不发送整个release或LaTeX源交接包，不再把ZIP重复压缩。

新增系统包/语言包/字体工具链0，全局配置修改0；已有复现依赖按授权保留。
