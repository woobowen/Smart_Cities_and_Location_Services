# Git、获取与复现

Repository: https://github.com/woobowen/Smart_Cities_and_Location_Services

Branch: `main`。起始提交 `677003de184b73a503f830a47186ee7688e13507`。最终审核提交以交付ZIP内 `FIXED_COMMIT.json` 和远程commit链接为准；本文件通过属于该commit来绑定版本，不在自身内容中制造自指哈希。普通push、不force、不改写历史，不删除旧实验一成果。

完整命令和边界见 [复现指南](../docs/REPRODUCIBILITY_GUIDE.md)、[环境变更](../docs/ENVIRONMENT_CHANGELOG.md)、[公开边界](../docs/PUBLICATION_DATA_BOUNDARY.md)。请分别确认：

1. Python/NumPy/SciPy/pymoo/Matplotlib版本和项目Kernel；测试与反例。
2. 从作者真实公开入口下载，固定ZIP SHA核验；精确转换NYC/TKY达到教师CSV同SHA，获取身份仍为作者重建。
3. 保持训练/验证/未来日期池、train-only司机prior、seed和预算；在独立目录重算，不覆盖当前审核run。
4. 只用公开聚合输入重画22正式图和2技术图；两本Notebook干净Kernel运行；报告源包独立编译。
5. 检查 `../evidence/research_data/local_only_manifest_current.json`、实际stage列表和发布审查：受限raw、可反解membership/事件/个体样本不入公开Git。清单hash可以公开，不代表原始记录已经上传。

本轮新增依赖均有日志；项目venv包与`.pth`/Kernel、用户级TeX包及tlmgr自更新分开登记，无apt、GPU、学校主机、付费API或`.bashrc`修改。清理需先核对后续重建影响，当前不删除依赖。

固定审核ZIP仅含该commit的审查核心文件及明确的远程索引，较大的全部工程通过同SHA读取；ZIP生成/远程验证回执属于交付后身份信息，存于包内及本地旁车，不倒写已冻结提交。
