本次为入口工程修复：帮助命令必须在实验导入前退出，既存输出必须拒写，复现实验须显式指定新的 `--output`（原 `--run` 方式仍可用，但目标必须不存在）。direct-file 与 `python -m task2.scripts.<launcher>` 均保留。

`original_sources/` 是真实历史源码快照，只用于核对旧 run 的 source hash，不能作为当前推荐运行入口。`source_hashes.json` 分别记录原源码与 guard 后源码；原模型、数值产物和审核身份不被改写为当前源码执行。

`validation_receipt.json` 记录55项隔离测试、20条当前workspace help命令、仅公共模型的 import/load_model/renderer-import smoke，以及所有受保护结果字节不变检查。`scientific_body_equivalence.json` 核对排除明确CLI/输出目录初始化后的科学语句AST及原library functions相同。本次未训练、评估、改参数或重画图。

原 `run_rl_final.py --help` 误触重放的完整证据仍在 `../replay_recovery/cli_help_replay_01/`，此处防护修复不把重放认作新独立实验。发布安全性仍须以实际Git索引的独立语义审核为准。
