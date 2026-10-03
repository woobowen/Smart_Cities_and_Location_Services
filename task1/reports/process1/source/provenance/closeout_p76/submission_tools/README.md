# 教师ZIP终检工具

`verify_teacher_zip.py`用于新生成的实际教师候选包。它执行CRC、安全成员、完整成员集合、逐文件字节/hash、两份正确PDF及25/77页数、两个完成版Notebook的结构/保存错误检查、Python语法及有限凭据模式扫描。

使用 `--probe` 时还在真实隔离解压目录调用现有包内 `verify_directory` 与 `static_probe`。后者只验证导入及冻结依赖，禁止模型调用、不运行轨迹。请由Codex用原科学Python环境执行。该脚本不发送文件、不运行FULL_RECOMPUTE，也不自动宣布Notebook Run All。

当前附带的12项测试是明确的合成验证器夹具，不是实际教师包，也不是实验结果。实际包的 `--probe` 分支须由Codex在本地完整仓库生成新包后执行，并将真实回执保存在本次任务evidence下。

`test_verify_teacher_zip.py`提供可复用的夹具测试，显式传入任意合法的25页/77页测试用PDF以及结果路径；夹具在临时目录删除，不进入教师包。
