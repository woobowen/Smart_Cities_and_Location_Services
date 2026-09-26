# PPTX source extraction: task1/作业/作业/build_ppt_agent/out/LLM辅助轨迹清洗评估智能体_架构与设计.pptx
Source SHA256: d456f082fcf65beef9e6ca4eb950b9ee1ac7d87a3a5e777e7ddd0325ebb1f82e
Classification: supplied teacher/starter material; saved outputs are historical, not current-run.
XML text and notes extraction preserves presentation slide order. Raster content requires separate visual inspection.

## Slide 1: ppt/slides/slide1.xml
任务三 · 架构与设计
LLM 辅助的轨迹清洗评估智能体
让 LLM 选工具、提参数，由确定性代码判定它的建议好不好
293 项测试 · 15 个工具 · 四层记忆 · 留出集消融

### Speaker notes
开场。这个框架要解决的问题是：让 LLM 参与轨迹清洗的参数决策，但它的建议必须能被自动判分，而不是靠人去读一段解释。整个设计围绕这一条展开。
1

## Slide 2: ppt/slides/slide2.xml
问题定义
为什么不能让 LLM 直接清洗
猜不准
LLM 没读过你的数据，dp_tolerance 说 5 还是 15 全靠语感
没法判分
「这条建议看着挺合理」不是判据，无法评价 11386 条轨迹上的建议质量
成本不可行
11386 辆车 × 每车多次 API 调用，烧不起
针对性解法：物理先验定边界、确定性搜索做标尺、分层记忆摊成本。
2

### Speaker notes
这三个问题必须讲透，否则后面所有设计看起来都像过度工程。猜不准、没法判分、成本不可行。特别强调第二点：没法判分是致命的，因为你无法评价 11386 条轨迹上的建议质量。
2

## Slide 3: ppt/slides/slide3.xml
设计约束
五条不可让步的设计原则
LLM 不碰数值，也不当优化器。
所有几何与统计计算在 core/ 里，是纯函数、可单测、不知道 LLM 存在。
LLM 不能写记忆。
工具清单里故意没有 write_memory，记忆写入只发生在核验确认有效之后。
坐标永不进上下文。
只传句柄和标量诊断卡，117 万点留在进程内存里。
提议与核验分离。
两个独立步骤，专门制造 generator-verifier gap。
core/ 不得依赖上层。
由 tests/test_architecture.py 用 AST 强制检查。
3

### Speaker notes
这是整个框架的骨架，后面每个模块都是为了兑现其中某一条。建议逐条讲清动机，尤其第二条（LLM 不能写记忆）和第四条（提议与核验分离）。
3

## Slide 4: ppt/slides/slide4.xml
结构
分层架构
共 10584 行，293 项测试全绿
4

### Speaker notes
强调依赖方向是严格的：core 不知道上面任何一层的存在。好处是学生能单独复用算法、敏感性实验不用启动智能体、智能体的 bug 不会污染算法正确性。这个约束由测试强制。
4

### Embedded images
- `ppt/media/image-4-1.png` SHA256=62fadab9992d3dfccea4a4863d5f331a8ce717ec9098e7bfcc0189e9ad48010c

## Slide 5: ppt/slides/slide5.xml
执行流程
一条轨迹的完整生命周期
第 3 步与第 7 到 8 步之间是全部价值所在
5

### Speaker notes
核心页。走一遍八步。重点停在第 3 步和第 7 到 8 步之间：那里把 LLM 建议质量变成了一个数字。其余步骤都是为了让这个数字可信而存在的支撑。
5

### Embedded images
- `ppt/media/image-5-1.png` SHA256=fbf6213086601fdecb3a813c7b53cec94e3b3f9fdef65bee67e0554ec6b6e071

## Slide 6: ppt/slides/slide6.xml
机制
核心机制一：regret 让建议可判分
regret = score（搜索最优）− score（LLM 提议）
它需要 ground truth，而 ground truth 来自确定性搜索。
联动：任务二的敏感性实验产物，就是任务三目标函数的地形图。
实测一条：提议 0.6008、基线 0.6330、最优 0.6366，得 regret 0.0358。
6

### Speaker notes
regret 需要 ground truth，而 ground truth 来自确定性搜索。这里有个联动值得指出：任务二的敏感性实验产物就是任务三目标函数的地形图。三种口径必须显式标注，否则会得出错误结论。
6

### Embedded images
- `ppt/media/image-6-1.png` SHA256=cd66fab0824a3934e4408c9291db06adfdd82965c026d14da6f58e847553e861

## Slide 7: ppt/slides/slide7.xml
机制
核心机制二：句柄与诊断卡
117 万点不可能进上下文。
LLM 只拿到句柄字符串和一张标量诊断卡。
诊断卡约 400 到 600 字节，11386 条全量也只有几 MB。
每次变换产生新句柄并记录血缘，trace 可完整重放。
TrajHandle(
  vehicle_id='246',
  version=3,          # 每次变换递增
  n_points=106,
  state_hash='a3f...' # 内容指纹
)

# 诊断卡字段（无任何坐标）
regime: moving
timeline.quality: ok
dt_bimodal: false
dup_ratio: 0.019
speed_p99: 100.77
anomaly_counts: {...}
7

### Speaker notes
上下文纪律。117 万个点不可能进上下文，所以只传句柄和标量诊断卡。血缘链让 trace 可以完整重放，也让结果可追溯。
7

## Slide 8: ppt/slides/slide8.xml
机制
核心机制三：四层记忆
L2 给数字锚点，L3 给物理直觉，两者不重复
8

### Speaker notes
重点是 L2 和 L3 的分工。L2 是机器算出来的统计区间，L3 是人写的因果解释。两者不重复：L2 给数字锚点，L3 给物理直觉。硬规则是 agent 对 vault 只读，这样它的 bug 不可能损坏知识库。
8

### Embedded images
- `ppt/media/image-8-1.png` SHA256=ed9ca0d26a843e6a9a3af5c7866bcf37bf5613178477afbab842f3d6f02d3969

## Slide 9: ppt/slides/slide9.xml
机制
核心机制四：三段式调参
dp_tolerance 区间 [0.5, 30] 米，上限约等于 GPS 精度 CEP。
dt_threshold 区间 [15, 180] 秒，下界保住正常的 20 秒采样。
dist_threshold 由 dt × 限速 × 安全系数推导，不由位移分布推导。
9

### Speaker notes
回答「参数怎么调」这个核心问题。LLM 不是优化器，它只给起点和方向。expected_effect 是白送的评分抓手，核验器只需比对符号。
9

### Embedded images
- `ppt/media/image-9-1.png` SHA256=5cbde85ee6f1a7c4a665d3a5c19491d768f1d5d0b99d073c8e221224aef7c71b

## Slide 10: ppt/slides/slide10.xml
接口
工具层：LLM 的全部能力
类别
工具
说明
只读（9 个）
load · profile · detect_anomalies · evaluate · compare_handles · find_knee · suggest_param_range · query_memory · query_playbook
不改变状态
产生句柄（6 个）
split · clean · simplify · apply_road_constraint · run_search · render
写入句柄存储
刻意缺席
write_memory · write_playbook · 任何 delete_*
LLM 无权写记忆
有一条测试专门断言工具名里不含 write、save、delete。这是设计，不是遗漏。
10

### Speaker notes
逐类讲工具。特别强调刻意缺席的 write_memory：这不是遗漏，是设计。有一条测试专门断言工具名里不含 write、save、delete。
10

## Slide 11: ppt/slides/slide11.xml
方法论
消融实验的两个方法学陷阱
陷阱一：信息泄漏
在评测轨迹上边跑边攒记忆，agent 会把「这条轨迹自己的上次结果」检索回来当先验。
等于考试时把答案摆在桌上。
三处强制：两阶段评测、read_only 不写回、exclude_self 排除同 seg_id。demo 与 holdout 重叠直接抛错。
陷阱二：模式标签造假
search-only 若仍调用 LLM，与含 LLM 的模式就不可比。
用 use_llm=False 真正跳过，并有测试断言其 LLM 轮次为 0。
regret 口径随模式变化，关闭搜索时是绝对口径，不能与归一化口径直接比较。
两者都会让消融表得出完全错误的结论，而且都是隐蔽的
11

### Speaker notes
这一页是方法论价值所在。信息泄漏和模式标签造假都是很隐蔽的错误，做错了两者都会得出完全错误的结论。我们是用代码强制避免的，不是靠自觉。
11

## Slide 12: ppt/slides/slide12.xml
实测
真实结果：记忆层没有带来可测增益
三种含 LLM 模式的提议分逐位相同。
根因已定位：
phase 1 准入的 5 条里，4 条静止、1 条 mixed。
moving 类轨迹在记忆里没有已验证案例。
4 条 moving holdout 检索到的区间数是 0。
瓶颈是 demo 集只有 12 条，不是设计失败。
如实报告：当前配置下不能声称记忆有效
12

### Speaker notes
必须如实报告。三种含 LLM 模式的得分完全相同。根因已经定位到具体层面：moving 类轨迹在记忆里没有已验证案例。这不是设计失败，是数据饥饿。
12

### Embedded images
- `ppt/media/image-12-1.png` SHA256=e139c125fb29aea49291d1bca95cd80263a9f9ad8c098e9f50da515879b48ed3

## Slide 13: ppt/slides/slide13.xml
工程发现
六个被数据推翻的假设
问题
实测症状
修法
墨卡托放大距离
31°N 系统性偏大 17%，容差预算凭空偏 17%
换局部等距投影
Hausdorff 口径错
顶点集算法给 548 米，真实值 4.77 米
改点到折线
DP 偏差估计错
tol=2 米时报出 8349 米
从递归结构取精确界
在噪声上算航向
单条静止轨迹假掉头 37 个
加 10 米噪声地板
漂移用绝对偏移
误判 50% 的正常行驶点
改无量纲曲率
毛刺用位移法识别
一处毛刺污染两位，真毛刺抓不到
改相对插值位置偏差
每条都配了回归测试，详见 DECISIONS.md
13

### Speaker notes
这页对做工程的人最有价值。每一条都是真实踩过的坑，而且都配了回归测试。可以挑两三个讲透，比如墨卡托 17% 和 Hausdorff 548 米对 4.77 米。
13

## Slide 14: ppt/slides/slide14.xml
边界
当前状态与已知短板
已完成
10584 行代码，293 项测试全绿
15 个工具、四层记忆、六类报告图
离线 Mock provider 可完整跑通
接真实模型只需设一个环境变量
已知短板
记忆层无可测增益（数据饥饿）
尚未用真实 LLM 跑过消融
路网仅有协议与离线实现
未全量跑 11386 条
Mock provider 每次给出同一个 knee point，天然抹平模式差异。不接真实模型，消融表就没有信息量。
14

### Speaker notes
诚实交代边界。已完成的部分和已知短板要分开讲，不要把短板藏起来。
14

## Slide 15: ppt/slides/slide15.xml
改进方向
下一步
1
扩大 demo 集到 200 条以上
让 moving 类轨迹积累到足够样本。这是当前最紧的瓶颈。
2
接真实 LLM 重跑消融
真实模型的提议有方差，才能显出搜索兜底与记忆先验的价值。
3
放松准入阈值做敏感性扫描
观察准入率与记忆增益的权衡曲线，这本身就是个好实验。
按预期收益排序。第一条不解决，后面两条的结论都不可信。
15

### Speaker notes
三条改进路径按收益排序。第一条最紧，第二条才能让消融表真正有信息量。
15
