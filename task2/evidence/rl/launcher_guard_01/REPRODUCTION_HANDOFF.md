当前防覆盖入口支持 direct-file 与 `python -m task2.scripts.<name>`。`--help` 不导入实验；目标已存在（含悬空symlink）会拒绝。需要复算时指定新的 `--output PATH`，不覆盖本轮成果。

- `run_rl.py --phase … --data DATA --run UNIQUE` 保留原参数形式，另可用 `--output PATH` 替代 `--run`。训练/评价数学函数与冻结版本相同。
- `run_rl_followup.py --phase … --model MODEL --output PATH` 保留显式父模型；`--run UNIQUE` 也保留。
- 其余固定实验launcher新增 `--output PATH`。该参数仅改变输出根目录，原冻结父模型/数据池/contract/seed/预算路径与数值定义不改变。更换父模型或整套重算须在独立工作副本准备同样相对路径；不能把改输出目录等同于已实现任意新父模型的调度系统。
- `resume_rl_rngfix.py --phase sensitivity|double --output PATH` 保留历史有效Q模型继承规则；原目录不再作为可覆盖resume目标。
- `diagnose_rl_double.py --output PATH` 仍读取 `task2/results/rl/double_v2_rngfix/` 的原模型与trace，并按原规则回退到旧Q模型。新的描述性诊断写到 `PATH/value_bias_diagnostics.json`。现有已接受绘图读取正式旧诊断路径，不自动接入这份新文件。新目录用于单项重算核对；要整体重建，须用独立工作副本及其相对路径，不能把原目录复制或替换作为本轮又一次新实验。

本次实际验证范围是入口保护、科学代码AST同等、公共模型载入与绘图模块import，未执行新的训练/评价，也未宣称干净Git clone里所有29模型与115个EA任务已通过单命令整套重算。原源码快照用于历史source hash追溯，不是推荐的CLI入口。
