# Goal 1 材料读取入口

这里只保存 `SC-LAB1-G1-FOUNDATION-001` 的材料核查。三角色运行证据、当前实现、实际验收与发布状态位于上级 Goal 1 审核包。本子任务未修改教师材料、starter、治理或其他 evidence，未 commit，未调用真实模型。

- [发现、方法歧义与影响](findings.md)：数据语义、六项初始值、历史线索逐项核实和 G1 处置边界。
- [R01–R16 来源表](requirements_sources.md)：教师页码、Notebook 单元、用户/项目要求和阶段映射；只核实材料，不宣布实验完成。
- [实际读取覆盖](reading_coverage.json)：文档/图表检查、真实命令、未执行/转交主线程的检查。
- [材料提取索引与哈希](extraction_index.json)、[starter 函数与文档目录](source_catalogue.md)：69 个相关文本文件，原代码保留在原位。
- 教师主 PPT：[43 页文字、公式、备注](pptx_05_text_and_notes.md)；补充 PPT：[学生讲义 16 页](pptx_01_text_and_notes.md)、[架构设计 15 页](pptx_02_text_and_notes.md)、[LLM 方法 14 页](pptx_03_text_and_notes.md)、[其同字节副本](pptx_04_text_and_notes.md)。
- Notebook：[基础预处理 source/count/outputs](notebook_02_source_outputs.md)、[LLM 示例 source/count/outputs](notebook_01_source_outputs.md)。保存的输出一律为 HISTORICAL，不能作为本轮运行。
- 去噪歧义：[构造脚本](direction_ambiguity_fixtures.py)、[带步骤的实际断言结果](direction_ambiguity_fixtures.json)。这是 CONSTRUCTED_FIXTURE，不是批准教师数据使用某种 schedule。
- 历史案例核对：[只读脚本](check_historical_cases.py)、[当前 JSON 的结构结果](historical_case_structure_check.json)。已暴露的案例须进入开发范围，不是独立确认集。
- [本材料目录最终核对](verification.json)：原来源哈希未变、JSON/Python 静态解析和本地 Markdown 链接检查；不是算法或质量验收。

重建文字提取：

```bash
python3 task1/evidence/goal1/materials/extract_materials.py
```

图表读取用 LibreOffice / pdftoppm 临时渲染，以及原包中的技术图片、GIF 和 Notebook 内图；命令与覆盖页见 reading_coverage.json。临时渲染仅用于核查，未作为新实验图复制。未安装任何依赖、未改变系统配置。
