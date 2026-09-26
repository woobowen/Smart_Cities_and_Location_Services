# 实际输入与分类

主数据 `task1/作业/作业/traj_dict.json`：44,809,130字节，SHA256 `c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3`。与 `utils/traj_dict.json` 逐字节相同，ZIP对应成员也相同。[原始hash检查](raw_integrity.json) / [ZIP对应关系](zip_byte_comparison.json)。ZIP108文件中104个已有解压文件一致、0个已有文件不同，另外4个为checkpoint/元数据/cache未解压项，未擅自删除或重新生成教师材料。

[全量结构摘要](structure_summary.json)和[逐记录结构表](record_profiles.csv)由原始JSON只读遍历得到：11,386记录、1,173,410点、1,162,024相邻边；全部时间/2D坐标对齐有限；0负dt、42,185零dt、29,175同时间不同位置、575,278相邻重复位置、8,272个dt>30秒。点数范围20–229。没有据此计算物理速度/米制距离，没有全量正式清洗或模型调用。

[材料清单](materials.json)登记实际路径、类别、用途相关位置、字节与hash。详细阅读覆盖见[材料读取清单](../materials/reading_coverage.json)、[治理/模板读取](../materials/governance_reading.json)和[材料入口](../materials/README.md)。只登记hash不等于声称每个辅助二进制都被全文理解；被要求的PPT/Notebook/方法source具有明确读取记录。

教师PPT/ZIP/data/starter属于teacher-provided/starter；Notebook原保存outputs、demo_out、历史报告属于HISTORICAL/demo，不能成为本轮结果。构造反例为CONSTRUCTED_FIXTURE；工作代码、真实原始诊断和调用回执另存本轮目录。两份P2参考PDF仍为模板，不是本轮正式报告。

7条开发pilot在模型反馈前写入[固定清单](../../../config/pilot.json)并随代码提交；包含已在starter详细暴露的0/246/256/306/352，再取前两个其他数字ID1/2，无成功筛选。全量结构盘点造成的暴露已记录，不称最终未见测试集。其他历史暴露209另有记录。本轮没有冻结最终留出比例。

执行结束[117个原始材料hash](../validation/original_integrity.json)全部不变，包括active治理、模板和installed plotting Skill。三份用户提到但本地未找到的研究文件不补造，见治理读取记录。
