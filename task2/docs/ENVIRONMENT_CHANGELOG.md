# 本轮环境与依赖改动

所有Python安装均在原有项目`.venv`内。未安装apt系统包，未用远程GPU/付费模型API，未改.bashrc/PATH/系统Python。字体原已存在，不分发独立字体二进制。

## Python（新增或项目内覆盖）

- 直接：pandas2.2.3、libarchive-c5.3、pymoo0.6.1.6、Matplotlib3.10.8、kiwisolver1.5.1、python-dateutil2.9.0.post0。
- 依赖：tzdata2026.6、moocore0.3.2、autograd1.9.1、cma4.5.0、Deprecated3.0.1、alive-progress3.3.0、about-time4.2.1、graphemeu0.7.2、wrapt2.5.2、cffi2.1.1、pycparser3.12。
- NumPy初始1.26.4；首次pandas未设上界升级到2.5.4而与原SciPy冲突，记录失败后恢复/固定1.26.4，并固定pandas2.2.3。没有把失败环境的collection声明为测试通过。
- 初始Matplotlib3.6.3与已存在IPython9.17.1的backend2gui移除不兼容。实际fresh-kernel失败后，项目内覆盖为3.10.8；系统原包保持。继承system-site-packages时旧mpl_toolkits又覆盖3D，已在本venv写`smartcities_matplotlib_namespace.pth`，真实Axes3D smoke与正式3D图通过。
- 专用kernel配置位于`.venv/share/jupyter/kernels/smartcities_dispatch/`，未安装全局Jupyter kernel。

实际日志：`evidence/research_data/pip_install.txt`、`evidence/dependency_repair.txt`、`evidence/notebook_dependency_repair.txt`；依赖约束见requirements.txt。Python环境全量版本快照另保存用于版本追溯。

## TeX工具链

沿用用户已有`~/.local/texlive/2026`。新直接包仅`placeins`、`needspace`。
首次安装被包管理器要求自更新中止；只更新texlive.infra/tlmgr（实测revision80721），没有`update --all`，随后两个直接包安装成功。

实际日志：`evidence/tex_package_install.txt`（失败原件）、`evidence/tex_manager_self_update.txt`、`evidence/tex_package_install_after_manager_update.txt`。

## 配置范围与清理

新增配置仅项目venv内的kernel/namespace修复及本任务的公开排除清单；根.gitignore仅补用户明确要求不公开的两个含数据ZIP。原始数据、有效实验、报告和可复建依赖保留，不因一次性交付自动删除。

这些依赖用于后续重建与审查，建议保留；若用户选择清理，再核对其对原实验一和本轮成果复建的影响，不能盲目删整个共享venv或回退全局TeX。

## 2026-11-06 Process 文档同步

新增系统包、Python 包、TeX 包、字体或工具链：无。沿用已有 `.venv`、TeX Live 2026 与 Poppler；未修改 `.bashrc`、PATH、系统字体或持久化 Fontconfig 配置。Process 构建脚本仅为其编译子进程生成临时 `FONTCONFIG_FILE`，排除竞争的 Noto Sans CJK Black，以匹配获批 PDF 的 Bold；临时配置随隔离构建目录清理。完整入站包和来源证据保存在仓库外私密暂存区，属于保留的真实性材料，不作无关清理。
