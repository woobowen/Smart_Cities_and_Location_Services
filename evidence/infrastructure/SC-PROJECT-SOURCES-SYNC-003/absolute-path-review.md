# 发布前绝对路径复核

`publication-audit.json`初扫检出的27处候选文件已分类检查（本说明后来新增的路径引用另计）：本轮编译/C/依赖日志保存真实临时目录与环境路径；测试使用临时fixture；当前README的`/tmp/...`是可替换的输出示例；旧同步README保存历史命令事实。同步器与新报告构建入口使用仓库推导路径，没有新增个人主目录依赖。

新ZIP中两个原样继承的数值provider含原有`/tmp/sc-g1-codex-0.157.1/node_modules/.bin/codex`默认可执行文件路径，分别为`task1/workflow/provider.py`与`g2_provider.py`。它们属于已有LIVE模型调用配置，逐字节继承旧真实FULL包；本轮不调用或改写，不把这一历史默认路径描述为新报告编译依赖或已新验证的LIVE环境。具体包继承与隔离门禁范围见[C包审核](c_review/independent-package-review.json)。

此记录完成路径审核，不扩大为数值provider迁移任务。日志中的真实路径也不为外观统一而改写。
