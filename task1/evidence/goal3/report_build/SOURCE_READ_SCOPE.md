# 本轮报告的实际来源读取

报告作者角色：B delivery/report engineering。只核读下列 3 个计划实际引用的主来源，未开展新广泛文献检索，未分发论文全文。

| 引用键 | 本轮实际读取 | 可支持的命题 | 不支持的宣称 |
|---|---|---|---|
| `proj-cart` | PROJ 官方 `Geodetic to cartesian conversion` 页面可见全文，HTTPS 200 | 经度、纬度、椭球高到地心直角坐标的转换语义；显式椭球参数 | 原始数据属于某 CRS、输入 datum 已证实、测量精度已知 |
| `proj-topocentric` | PROJ 官方 `Geocentric to topocentric conversion` 页面可见全文，HTTPS 200 | 固定原点的 E/N/U 定义；地理输入先 cart 再 topocentric | 局部平面处处等同测地距离；源 datum 或道路定位正确 |
| `cawley2010` | JMLR 官方摘要与文献元数据，HTTPS 200；未读全文 | 有限样本的模型选择准则可能过拟合，使性能评价产生选择偏差；据此说明分开选择与确认的一般动机 | 本实验样本量、阈值、置信保证来自该论文；完整复现或完整理论核验 |

URL、下载字节数、HTTP 状态、SHA256 与真实请求时间见 `source_fetch_receipts.json`。网页工具两次返回连接失败后没有继续重试，改用现有 Python urllib 向相同官方 HTTPS 地址读取，未绕过 TLS、未安装依赖。临时网页文本仅保存在 `/tmp` 用于实际阅读，不纳入仓库或教师包。

课程方法定义另依教师 `实验课1.pptx` 相关原件页与已核验 starter 映射，见 `../teacher_mapping.json`。真实统计、参数、模式、记忆与 AI 引文依 G1/G2 保存产物，历史版本身份在正文明确列出，不将已保存结果写成本轮重新运行。

本轮没有声称完整核读既有 Source Audit 中全部论文；不引用未经本轮核读全文的具体定理或算法性能结论。引文少于 2–4 篇论文不作为缺项：当前用户明确允许只借鉴思想或不采用论文算法。
