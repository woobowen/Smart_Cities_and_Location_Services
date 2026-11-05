本目录记录 `/root/reinforcement` 对主线程 Notebook、发布过滤、公共绘图输入和报告源包的独立集成检查。此前本人编写的 RL 算法/图表自检不改称独立数学核验；该数学核验见 EA 的独立回放。CLI guard 的作者验证另在 `evidence/rl/launcher_guard_01/`，独立追加由 R 负责。

- `notebook_fallback_review.json`：核对两份正式 Notebook 实际 fresh-kernel 执行计数、原教师测试、300 episode 训练输出、active run 及结果 hash。本人未重复 Run All，不将读取已有结果称作新训练。
- `public_notebook_generator_review.json`：无原 ZIP 的隔离目录实际生成两份 Notebook，code cells 与已执行版本相同；fallback 使用可公开教师原 starter。
- `content_probe.json` 与 `sensitive_classification.json`：真实匿名 membership+F 可反解逐单 fare 的风险验证，仅保存方程数、rank、误差，不保存恢复值；完整逐条输入/动作选择本地保留。
- `public_projection_review.json`：原124项公开投影独立核对，1,024,816个数值叶子保持，membership/context去除。该旧审核保留原 hash；之后 final REPLAY 的唯一公开front runtime绑定变化由 `independent_ea_on_rl/replay_review/public_binding_result.json` 追加，不追签旧 bytes。
- `public_rl_render_review.json`：真实隔离、无私有CSV/episode/trace/ZIP，仅公共模型/aggregate输入，12张PNG逐字节相同。guard 引入新stdlib helper 后只追加模型载入/绘图模块 import smoke，不重复重画。
- `exact_public_data_review.json`：独立从已验证公开ZIP实际转换两城市CSV，字节等于教师输入，8份DataFrame及8项receipt/优先级/安装案例通过。没有再次请求网络；R 的真实网络获取回执单独保留。
- `report_source_01/compile_comparison.json`：旧0215源包实际隔离 XeLaTeX 编译26+8页，全文和34页200dpi像素与交付PDF相同，PDF二进制因元数据不同。当前c386源包的81成员编译资产同等由 `independent_integration_index/result.json` 追加核对；源包后续仅 provenance 变化可按同样精确成员检查继承。实际页面视觉审核归 R 的 `independent_report_review/pdf_final_review.json`，本人不把像素同等冒称新增逐页目视。
- `staged_semantic_inventory.json` 保留初轮实际index快照及发现；其中真实 `km_timing` membership 漏项已 exact 排除，见 `staged_sensitive_addendum.json`。原件仍本地。
- `staged_semantic_review.json` 审第二轮3518实际staged blobs，集合hash `8554be1629ed082210872fc00745fec358b71e1e0abb1171908e5bcf1ca223ba`：39NPZ、11CSV、所有JSON及Notebook输出、125syntheticinputs、31SVG、41PDFtext、156textlogs按内容核对。64原log复制字节全同，其中62staged、2build-cache排除。3个与本地目录hash相同的公共获取receipt逐内容确认为允许的aggregate provenance。

该回执限已记录index集合，不覆盖未审新增文件。后续 guard/独立审核/范围文字修复/sidecar与源包provenance变动应追加有界extension；未经实际blob检查不自动扩展PASS。远程发布、外部GPT审核、用户最终验收和教师提交由主线程继续，不属于本子角色的完成声明。本子角色没有新增安装依赖。
