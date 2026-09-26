# 探针适配说明

交接原脚本保持原样。probes_after.json 是未修改脚本在 CODE 157b79d 上的真实结果；新增可执行文件存在性检查使其两项 provider 测试先在假路径处被拒绝，未抵达 run_limited 的注入点。不能把它当作 timeout 注入路径已测通过。

reproduce_findings_adapted.py 唯一变化：将 provider.executable 的不存在假路径替换为 sys.executable（实际存在）。run_limited 仍由原脚本 mock 成 OSError 或 TimeoutExpired，不会启动 Python、CLI 或模型。所有反例和断言均保留；适配只是跨过新增路径前置校验。对应 probes_after_adapted.json。
