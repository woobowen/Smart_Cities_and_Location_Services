# 本轮实际修改与继承

- `AGENTS.md`从received按原字节导入；release本来已是本轮批准新稿，不由旧active覆盖。其余四个active和五份release载荷均未重写。五规范中只有AGENTS相对89371f6变化。
- `sources.json`仅AGENTS成员的Revision/hash/本轮变更来源更新；其他15项完整对象不变。集合批准仍承接SYNC-003，顶层增加本轮集合核验与当前UI交接位置。
- 原`sync_sources.py`仅`instructions_text`调整当前UI交接和历史说明；其余模块AST相同。SOURCE_MANIFEST/UPLOAD_INSTRUCTIONS由该同一生成器产生，没有手工维护新manifest或修改安全更新逻辑。
- `task1/README.md`、Goal3 `REVIEW_PACKET.md`当前区、`TECHNICAL_HANDOFF.md`当前前缀区分非Process关闭、旧二审和当前新提交待审。两个历史正文保留原字节；用户已确认复盘/25页文稿，同时不新增Understanding/VIVA签署。
- 根README与报告工程README仅调整当前入口、历史构建/依赖语境和Process责任说明；报告章节、图、PDF、源ZIP、生成器、包和数值文件不变。
- SYNC-003原REVIEW_PACKET仅在末尾追加后续二审承接；external_review保存用户转交来源和真实接收时间。原报告附件尚未入库，不创建伪原件；原FINAL_RESPONSE、C意见、测试、PUBLICATION_RECORD均不改。
- 新增本任务Prompt、received、起始保护、迁移/验证/C/发布与交付记录；不创建长期plan/design doc、Settings长稿、Evidence Plan或第二套状态平台。
- 5个已确认Windows ZoneTransfer元数据保留原字节/mtime后移至本任务隔离目录；可发布记录保存来源、hash和base64。没有删除有效项目文件。

作者核验以[author-verification.json](author-verification.json)为准：6679项起始保护中6663项不变、11项授权更新、5项元数据迁移；[protection-check.json](protection-check.json)列出具体变化。新文件的发布前检查单独记录，不将它们冒称起始对象。

新增实验模型调用=0，数值运行=0，报告编译=0，包构建=0。历史FULL、报告构建及网页GPT18项检查均保留原身份。placeins/needspace保留；没有新增或清理系统包、语言包、工具链、字体、认证或全局配置。
