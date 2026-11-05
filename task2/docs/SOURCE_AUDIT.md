# Source Audit

实际审读与检索者：`/root/research_data`，Task R-001。检索日期：2026-11-05（America/New_York用户时区）。主线程及其他Agent新增来源应追加自己的实际支持关系，不把浏览摘要冒称全文审读。

| 来源 | 作者/机构；日期；类型 | 可访问性与实际支持范围 | 本任务采用/边界 |
|---|---|---|---|
| [Foursquare Dataset 原作者入口](https://sites.google.com/site/yangdingqi/home/foursquare-dataset) | Dingqi Yang；页面无明确发布日期；作者发布页 | 实际打开；NYC/Tokyo签到、时戳/GPS字段、研究用途与引用文献；网页列NYC227428/TKY573703 | 数据身份是签到，不能称真实网约车订单；网页未列明确再分发license，引用要求不等于明确的再分发授权 |
| [原作者数据readme](https://drive.google.com/file/d/1mH3w4XrqoZK393gtvi5LlKmMPqLpnYK8/view?usp=sharing) | Dingqi Yang；Drive元数据修改2024-11-07；原始readme | 网页仅登录页；随后实际使用Google Drive `fetch`读取成功。八列：匿名user、venue/category、lat/lon、timezoneOffset分钟、UTC。要求引用Yang et al. TSMC45(1):129–142,2015 | 支持逐记录UTC+offset的local civil clock定义；未证明WGS84 datum。readme写TKY537703，而实际文件与网页均573703，保留为来源文本差异 |
| [原作者数据ZIP](https://drive.google.com/file/d/1VE67jfSN-GV6fkCfuyBEQJzk_qy-SfOk/view?usp=sharing) | 原作者下载入口；公开Drive存储 | 链接由作者网页实际click得到；早期两次完整下载后，新版又于11:33:19 UTC无缓存网络下载，均核验25,546,284字节、ZIP SHA256 `cbe3fdab373d24b09b5fc53509c8958c77ff72b6c1a68589ce337d4f9a80235b` | 早期float10g转换有末位差，保留历史；后续直接Decimal half-up10位+CRLF间隔/末行无换行已重建两城市teacher相同字节，仍标作者获取来源。脚本、hash与边界见PUBLICATION_DATA_BOUNDARY |
| [NSGA-II原论文](https://dynamics.org/~altenber/UH_ICS/EC_REFS/MULTI_OBJ/DebPratapAgarwalMeyarivan.pdf)；[作者机构书目](https://research.birmingham.ac.uk/en/publications/a-fast-and-elitist-multi-objective-genetic-algorithm-nsga-ii) | Deb, Pratap, Agarwal, Meyarivan；2002-04；IEEE TEVC6(2):182–197；原论文/机构记录 | 检索取得原文摘要与机构DOI 10.1109/4235.996017；非支配排序、精英合并、spread保留 | 支持算法机制，不支持本任务NSGA优于KM的实测结论 |
| [NSGA-III Part I DOI](https://doi.org/10.1109/TEVC.2013.2281535)；[DEAP官方示例](https://deap.readthedocs.io/en/stable/examples/nsga3.html) | Deb/Jain；2014；IEEE TEVC18(4):577–601；官方实现文档 | 原作者PDF `https://www.egr.msu.edu/~kdeb/papers/k2012009.pdf`实际打开返回503；官方DEAP检索页确认论文与reference-direction机制 | 三目标不构成必然胜出；本轮以teacher数学定义与独立测试为准，不能说完整原论文PDF已访问 |
| [SciPy linear_sum_assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) | SciPy官方；动态文档 | 实际检索到官方完整目标说明：最小总成本；矩形允许；modified Jonker–Volgenant实现 | 课堂可称KM/匈牙利型线性分配，但不宣称SciPy内部实现就是经典KM，更不能当成瓶颈匹配 |
| [Q-learning](https://doi.org/10.1023/A:1022676722315)；[原论文PDF](https://www.ece.uvic.ca/~bctill/papers/learning/Watkins_Dayan_1992.pdf) | Watkins/Dayan；1992-05；Machine Learning8:279–292 | 实际检索原论文摘要和出版页：表格Q学习及充分采样等收敛前提 | 不将本教学有限300episode/学习率下限视作已满足理论收敛条件；半马尔可夫折扣按teacher定义检查 |
| [Double Q-learning](https://proceedings.neurips.cc/paper_files/paper/2010/hash/091d584fced301b442654dd8c23b3fc9-Abstract.html) | Hado van Hasselt；NIPS2010；原会议论文页 | 实际打开摘要；双估计分开选择/评价，针对max估计正偏差，也可能低估 | 不保证消除多人竞争模型失配，不能事先保证本任务收入改善 |
| [Large-Scale Order Dispatch](https://doi.org/10.1145/3219819.3219824) | Zhe Xu et al.；2018-07-19；ACM KDD:905–913 | 实际检索ACM出版页摘要：历史时空价值+实时组合分配，兼顾即时与未来收益 | 用作teacher Q-KM的思想来源；本Notebook表格Q不是该工业系统等价复刻，不外推其线上收益 |

## 数据公开同步边界

作者官网和readme均提供下载与引用要求，但未找到明确允许再分发的license。现有证据**未证明禁止本地教学使用**，也**未证明允许本仓库再次公开分发**。不把目前Foursquare API商业条款倒套到2012–2013研究数据。

用户后续已明确没有额外许可，因此按本次明确发布边界不公开根目录两份含数据ZIP、基础嵌套ZIP/RAR、NYC/TKY原始CSV及可还原逐记录的派生。保留本地完整输入、SHA256、来源入口和重建脚本；代码、配置、测试、聚合指标、方法、审查记录、图与双报告继续公开制作。独立V-PKG又发现匿名membership+总目标可以线性反解逐单fare，不能只凭删ID或扩展名判断；具体内容分类与exact list由PUBLICATION_DATA_BOUNDARY承接。

## 文件事实与网页差异

- teacher NYC文件227428条、TKY573703条，与作者网页一致；原readme东京数写537703，记录为来源文本差异。
- 作者网页/readme称从12 April 2012，teacher NYC最早UTC为2012-04-03T18:00:09Z，TKY为2012-04-03T18:17:18Z。按实收文件保留，不人为截掉前九天制造一致。
- 两城市经纬度是角度数值与GPS语义；datum无独立文件证明，因此source_crs=UNVERIFIED。教学NYC局部平面模型是分析假设，不是新赋的来源CRS标签。
- 原始offset值不只NYC常见-240/-300、TKY540；按原字段构建local clock会有异常代理。详见时间审计说明。
- 源入口公开fallback先保留了历史近似AUTHOR_RECONSTRUCTED，其旧隔离回归为`source_entry_regression.json`。后续发现直接half-up和末行序列化规则，新版真实网络重建两城文件hash均等于teacher。新版同时核对内容hash与获取/变换来源，区分TEACHER_PROVIDED、AUTHOR_RECONSTRUCTED_EXACT_BYTES和未知提供者的同字节输入，不因hash相同倒写提供者。8份DataFrame精确全等、所有日期分区和真实安装sidecar隔离回归见`source_entry_exact_regression.json`；原teacher和正式run CSV未更改。
- 独立`/root/reinforcement`随后实际用已验证缓存ZIP，在隔离root运行新版转换，核验两城输出hash、8份DataFrame精确全等及8个receipt/provider/teacher优先反例；结果`evidence/independent_package/exact_public_data_review.json`。该角色先发现仅凭author目录可绕过receipt，作者修复后复验通过。独立核验没有再次网络下载，真实新版无缓存下载仍归R-001作者动作，不混写身份。
- 教学局部平面误差核验使用4000个训练内点对，以WGS84椭球仅作数学比较模型；欧氏局部距离相对模型测地线最大观测偏差约0.585%，不构成source datum证明。Manhattan/Euclidean比值在[1,sqrt(2)]内，仍不能代表真实路网，见 `geometry_model_check.json`。
- 后续主线程独立扩大到全部25,550 OD，数学模型检查的最大相对偏差0.633%/绝对133.5m。正式报告采用全OD范围；这与上述训练抽样范围不同，不改写早期抽样检查，也不增加datum来源证明。
