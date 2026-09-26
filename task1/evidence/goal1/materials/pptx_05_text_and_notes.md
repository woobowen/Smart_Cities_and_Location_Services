# PPTX source extraction: task1/实验课1.pptx
Source SHA256: cf5fdbdd0e116818f4bf195e8761dd55c4733443d7c360c986cf1cdfddfda075
Classification: supplied teacher/starter material; saved outputs are historical, not current-run.
XML text and notes extraction preserves presentation slide order. Raster content requires separate visual inspection.

## Slide 1: ppt/slides/slide1.xml

实验课安排和考核方式


董宜滔 
20260917

### Speaker notes



### Embedded images
- `ppt/media/image7.png` SHA256=85e10e23a3dddc4ee140e1c66baea0c171c88fe136f30bf267aa989804524eb7
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image6.png` SHA256=7b4cf3aaa8948c9858dd7ebfbf9cdec6e3a147de2ad2c251bd09e029b785e4e1
- `ppt/media/image5.png` SHA256=f3fd0305b0d41ae96a8589425f06aaed96c56ef727d13e046338ec55d17a128e
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image4.jpeg` SHA256=52ee35a00838544ca89cd26635138deb108bc87b7e5b9b9446c714763bd9990a

## Slide 2: ppt/slides/slide2.xml

目录
课程介绍
课程内容
考核要求
时间安排
轨迹数据质量提升
轨迹数据预处理
基于LLM辅助的轨迹预处理自动化工作流
（基于LLM增强的轨迹数据质量提升智能体）

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 3: ppt/slides/slide3.xml

课程考核
结合理论课的内容布置实验
课程设计为位置服务与智慧城市某一应用问题的实现，需提交源码与实验报告，并进行答辩


可选应用问题包括但不限于（推荐自拟题目）：
  运输热点的提取                  交通供需预测
  路径规划		        智能派单
  空车调度                            时空数据管理
  
成绩计算方式：
考勤10%+实验作业30%+课程设计60%
请自行组成4人小组，源码中明确每位成员的技术分工

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 4: ppt/slides/slide4.xml

实验课内容
       
利用时空数据解决智慧城市场景下的真实问题
实验一：轨迹数据预处理
轨迹数据的分段、去噪、简化；轨迹数据预处理的评估
构建基于LLM 辅助轨迹数据清洗评估工作流
实验二：基于轨迹数据的停留点检测
基于时间、距离间隔阈值的停留点检测；基于方向聚类的停留点预测
基于不同聚类进行停留热点识别；构建 LLM 辅助热点分析工作流
实验三：交通流量预测
基于深度学习的交通流量预测
基于LLM增强的交通流预测
实践（课程设计）
运输任务分配
基于二部图匹配的运输任务分配
基于LLM的任务分配智能体

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 5: ppt/slides/slide5.xml

实验课内容
实验模块
对应大纲章节
核心产出
评分标准
实验一 轨迹数据预处理
第一章 智慧城市概述
轨迹数据清洗与压缩程序、数据处理评估报告、实验过程报告（包含AI批判）
完成基础任务60分+
完成拓展任务90分+
实验二 停留热点挖掘
第二章 智慧交通与应用
停留点检测与聚类程序、POI功能标注结果表，实验过程报告
完成基础任务60分+
完成拓展任务90分+
实验三 车货匹配
第三章 智慧物流与应用
车货匹配求解器程序、求解器性能报告、实验过程报告
完成基础任务60分+
完成拓展任务90分+
综合课程设计
第四章 智慧城市应用前沿
研究报告、可复现代码包、路演答辩


### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 6: ppt/slides/slide6.xml

实验课内容
【AI生成内容的准确性批判】提示词示例：“请为共享单车轨迹设计清洗流程并给出阈值。”
批判要求：检查其是否混淆速度单位、是否把经纬度直接当平面坐标、是否对缺失值做无依据插值；至少构造一组反例，记录修改前后指标，并说明哪些建议被拒绝以及原因。
【AI建议的隐含假设分析与批判】提示词示例：“AI建议‘缺失值用线性插值’，其隐含假设是‘轨迹在缺失期间匀速直线运动’，这个假设在什么情况下不成立？”
批判要求：可以主动向AI提问是否存在前提假设，也可以根据自己的思考对AI进行反问，相关内容需要写入实验报告。

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 7: ppt/slides/slide7.xml

课程设计时间安排
       
课程设计时间安排：
第二周 9月24日 确定人员分组
第五周 10月22日 开题答辩
第十一周 11月16日 中期进度汇报
第十六/十七周 12月31日/1月8日 最终答辩（待定）
 
https://developer.ecnu.edu.cn/vitepress/llm/model.html

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 8: ppt/slides/slide8.xml

课程设计时间安排
 
https://developer.ecnu.edu.cn/vitepress/llm/model.html
建议大家用deepseek harness

能不用codex、CC、KIMI CODE就不要用

### Speaker notes


### Embedded images
- `ppt/media/image11.png` SHA256=929d602db70d12549ddf9b5d32e1f422da0823ecbe746df23b63640c1322d443
- `ppt/media/image10.png` SHA256=881072ae26108b572020bf6c2c758868a0ac79de67d624b4170a2e6850725d75
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 9: ppt/slides/slide9.xml

轨迹数据质量提升


董宜滔 
20260917

### Speaker notes



### Embedded images
- `ppt/media/image7.png` SHA256=85e10e23a3dddc4ee140e1c66baea0c171c88fe136f30bf267aa989804524eb7
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image6.png` SHA256=7b4cf3aaa8948c9858dd7ebfbf9cdec6e3a147de2ad2c251bd09e029b785e4e1
- `ppt/media/image5.png` SHA256=f3fd0305b0d41ae96a8589425f06aaed96c56ef727d13e046338ec55d17a128e
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image4.jpeg` SHA256=52ee35a00838544ca89cd26635138deb108bc87b7e5b9b9446c714763bd9990a

## Slide 10: ppt/slides/slide10.xml

实验一-轨迹数据预处理
定义2：轨迹
       一条轨迹可以表示为tr= (𝑝1,𝑝2,…,𝑝𝑛) ，其中𝑝𝑖表示轨迹tr中第i个轨迹点。由于在一条轨迹中轨迹点是连续的，即每个点是按采样的时间顺序（时间戳大小）进行排序的，因此对∀𝑖 < 𝑗，满足𝑝𝑖.𝑡<𝑝𝑗.𝑡。
 
定义1：轨迹点
       一个轨迹点可以表示为𝑝𝑖= (𝑜𝑏𝑗𝑖,𝑙𝑛𝑔𝑖,𝑙𝑎𝑡𝑖,𝑡𝑖) ，含义是移动对象obji在时刻𝑡𝑖时位于<𝑙𝑛𝑔𝑖,𝑙𝑎𝑡𝑖>处。
 


### Speaker notes


### Embedded images
- `ppt/media/image13.png` SHA256=9ffcbe2f4ac1b0c8dab1917a71ed7c61fabfd36f84a2d18a49e58ba44c12333a
- `ppt/media/image12.png` SHA256=24118e7c694a0f4775ad0e84e69006a866f15b34b1994f2838916119ebf23c44
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 11: ppt/slides/slide11.xml

数据示例
𝑜𝑏𝑗𝑖=123
𝑙𝑛𝑔𝑖=121.4330462
𝑙𝑎𝑡𝑖=31.21349962
𝑡𝑖= 2018-03-20 21:39:40
 
𝑜𝑏𝑗𝑖+1=123
𝑙𝑛𝑔𝑖+1=121.4334155
𝑙𝑎𝑡𝑖+1=31.21379059
𝑡𝑖+1= 2018-03-20 21:39:50
 

### Speaker notes


### Embedded images
- `ppt/media/image16.png` SHA256=b6b4408d89d53a2a4eb6d3d18b39a28d804cc143bdf3d5882ff7e56ffc533dab
- `ppt/media/image15.png` SHA256=6b3d8e6595f3bca0098c2bebb94cf26d64ca73e8cba222f87bd8e7b86aed8ec6
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb
- `ppt/media/image14.png` SHA256=55618ec74b4f08352701b68702e4608be10156b27bfaf7d25b2b61757ed0341f

## Slide 12: ppt/slides/slide12.xml

数据示例
obj
time
lng
lat
17
2018/4/10 0:12:57
121.4742
31.25729
17
2018/4/10 0:13:07
121.4742
31.25729
17
2018/4/10 0:13:27
121.4742
31.25729
17
2018/4/10 0:13:37
121.4742
31.25729
17
2018/4/10 0:13:47
121.4742
31.25729
17
2018/4/10 0:13:57
121.4742
31.25729
17
2018/4/10 0:14:08
121.4742
31.25729
49
2018/4/10 0:00:00
121.4483
31.22085
49
2018/4/10 0:00:09
121.4483
31.22085

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 13: ppt/slides/slide13.xml

GPS坐标系
WGS84坐标系
       即地球坐标系（World Geodetic System），国际上通用的坐标系。设备包含的GPS芯片或者北斗芯片获取的经纬度一般都是为WGS84地理坐标系，目前谷歌地图采用的是WGS84坐标系。
GCJ02坐标系
       即火星坐标系，国测局坐标系。是由中国国家测绘局制定。由WGS84坐标系经加密后的坐标系。谷歌中国和搜搜中国采用的GCJ02地理坐标系。

### Speaker notes
通俗来讲，国内收集的GPS轨迹数据都是GCJ02坐标系的，而国际上的数据则普遍为WGS84坐标系，如open street map、bing等开源地图，在日常使用时。

### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 14: ppt/slides/slide14.xml

投影坐标系
平面坐标系，常以米为单位。球面是曲面，但我们的地图是画在平面上的，这里要有一个换算过程。采取的就是投影法。

比如墨卡托投影，用圆柱形的纸板将地球蒙起来，然后有一根蜡烛在地球球心，发光发热，将地球投射在这块纸板上，于是就得到了地球的平面图。

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 15: ppt/slides/slide15.xml

投影坐标系
对于墨卡托投影来说，越到高纬度，大小扭曲越严重，到两极会被放到无限大，所以，墨卡托投影无法显示极地地区

### Speaker notes


### Embedded images
- `ppt/media/image19.png` SHA256=209a885641f9ba02d36cb94206516aaca3b9feff1c05f53dcbee2029f3c11c6e
- `ppt/media/image18.GIF` SHA256=23d2806d703526c8864c8e14e91e85825c537fab7644ca440bf0b2c6a734cb48
- `ppt/media/image17.png` SHA256=5961d04f5ca12a0eb175c256af2f07421f8b6c7ac76a5366b25ba4fc577216ba
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 16: ppt/slides/slide16.xml

作业一-轨迹数据预处理

### Speaker notes


### Embedded images
- `ppt/media/image20.png` SHA256=4d5f0a46133205d26909334a1c8bc0dde8a54a13375a6ed17c7752fa79fbc09a
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 17: ppt/slides/slide17.xml

为什么需要轨迹数据预处理
背景：由于用户误关闭设备或者GPS设备故障导致相邻轨迹点的采样时间间隔远大于平均采样间隔
影响：相邻轨迹点连成的线段无法表示移动对象真实通行的路径
数据分析：相邻轨迹点的采样时间间隔远大于平均采样间隔；相邻轨迹点的位移距离远大于平均位移距离。
GPS信号中断
𝑝0
 
𝑝1
 
𝑝3
 
𝑝2
 
𝑝4
 
𝑡2−𝑡1=3𝑠
 
𝑡3−𝑡2=30𝑠
 
𝑝5
 
𝑝6
 

### Speaker notes


### Embedded images
- `ppt/media/image26.png` SHA256=c27293f4c5dfe5db4dadfda5c07a32041cc7d32403ffb8ebe7d12d866bc13b87
- `ppt/media/image25.png` SHA256=c7f53b9a17bef849d411998735a7e85c3da3c6a55d46296d2769805dd01b7125
- `ppt/media/image24.png` SHA256=c590d861b684ac84235ffc4e569d94f4f7520d2394a83d9fd57620129bc257bf
- `ppt/media/image23.png` SHA256=9ba9ba2cf2abeffcc50c5d07adc813c547dbf79b8be568bfd6ae9106421eeac8
- `ppt/media/image22.png` SHA256=480cc9c2598024a18294a79d45f439771bb582f42c8fce4d1967edd35d7d34b8
- `ppt/media/image21.png` SHA256=be916ac84af0858aa1af0182bf7f2af5bf6a18a5fa83311fc2d7b63caa2a6567
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image30.png` SHA256=aa61e669952f53910995e9b29c454bea4945c6a01adcb0b76c5546c80c0b5029
- `ppt/media/image29.png` SHA256=fa933038632c00fd260f511e1e504393114d94b2995acaa91dd7196a694249f7
- `ppt/media/image28.png` SHA256=f606b8fd2bda3bc6f0601cb6389c02a4856b9568e89fedeb4e51a12a70658b20
- `ppt/media/image27.png` SHA256=d7f8f99ecc1c41da875982618910d907863d4a4e302d3ceefcc590b68c91b3cb
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 18: ppt/slides/slide18.xml


为什么需要轨迹数据预处理
Step1: 定位距离异常、时间间隔异常的相邻轨迹点
解决方法：轨迹分段
Step2: 根据定位结果将轨迹分段为多条子轨迹
(𝑝2, 𝑝3)
 
𝑝0
 
𝑝1
 
𝑝3
 
𝑝2
 
𝑝4
 
𝑡2−𝑡1=3𝑠
 
𝑡3−𝑡2=30𝑠
 
𝑝5
 
𝑝6
 
Input：单条轨迹数据 tr={(𝑝0, 𝑡0),(𝑝1, 𝑡1),…,(𝑝𝑛, 𝑡𝑛)}
 
将tr划分为{(𝑝0, 𝑡0),…,(𝑝2, 𝑡2)}与{(𝑝3, 𝑡3),…,(𝑝n, 𝑡𝑛)}
 
Step3: 删除分段结果中距离过短或点数过少的子轨迹
删除{(𝑝0, 𝑡0),…,(𝑝2, 𝑡2)}
 


Output：tr={{(𝑝3, 𝑡3),…,(𝑝i, 𝑡𝑖)}, …{(𝑝𝑗, 𝑡𝑗),…,(𝑝𝑛, 𝑡𝑛)}}
 

### Speaker notes


### Embedded images
- `ppt/media/image25.png` SHA256=c7f53b9a17bef849d411998735a7e85c3da3c6a55d46296d2769805dd01b7125
- `ppt/media/image24.png` SHA256=c590d861b684ac84235ffc4e569d94f4f7520d2394a83d9fd57620129bc257bf
- `ppt/media/image23.png` SHA256=9ba9ba2cf2abeffcc50c5d07adc813c547dbf79b8be568bfd6ae9106421eeac8
- `ppt/media/image22.png` SHA256=480cc9c2598024a18294a79d45f439771bb582f42c8fce4d1967edd35d7d34b8
- `ppt/media/image21.png` SHA256=be916ac84af0858aa1af0182bf7f2af5bf6a18a5fa83311fc2d7b63caa2a6567
- `ppt/media/image31.png` SHA256=477499f3923666af0cebcea2acdd48c2a7211a9478888aed33e9f10716c9c39b
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image35.png` SHA256=1222c3d65ff93820244bbfb2fa52a798897a3f4baade5e798b21f827e95006ae
- `ppt/media/image34.png` SHA256=7a349ab7844b512105ac7ee5c37aa13194653768e2903a3550487c6e5d0d46a5
- `ppt/media/image33.png` SHA256=e47acb69d6f810853d57d1f5d2c4aa6ee9d5faa1982c196383f9b5578df5fcd2
- `ppt/media/image32.png` SHA256=7add7eae502343d22c34a270f64fee937de89c17851c2075581b25a44ef767ee
- `ppt/media/image30.png` SHA256=aa61e669952f53910995e9b29c454bea4945c6a01adcb0b76c5546c80c0b5029
- `ppt/media/image29.png` SHA256=fa933038632c00fd260f511e1e504393114d94b2995acaa91dd7196a694249f7
- `ppt/media/image28.png` SHA256=f606b8fd2bda3bc6f0601cb6389c02a4856b9568e89fedeb4e51a12a70658b20
- `ppt/media/image27.png` SHA256=d7f8f99ecc1c41da875982618910d907863d4a4e302d3ceefcc590b68c91b3cb
- `ppt/media/image26.png` SHA256=c27293f4c5dfe5db4dadfda5c07a32041cc7d32403ffb8ebe7d12d866bc13b87
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 19: ppt/slides/slide19.xml

为什么需要轨迹数据预处理
背景：由于信号干扰等原因， GPS设备采集到的轨迹点位置与车辆的真实位置之间存在较大差异。
影响：漂移点会被误识别为转向轨迹点，对后续路口识别、地图构建等任务产生不利影响。
数据分析：漂移点的方向与其前序、后序轨迹点的方向都存在较大差异。
GPS信号漂移

漂移点

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb
- `ppt/media/image36.png` SHA256=cf26213fdb53b56f0cc499342f631d7fbaee4ac2087be15355d8fc18d17eaff3

## Slide 20: ppt/slides/slide20.xml

为什么需要轨迹数据预处理

漂移点
解决方法：轨迹去噪

Step1: 计算每个轨迹点的方向：当前轨迹点与后序轨迹点连成线段的方向
Step2: 定位方向与其前后序轨迹点方向都存在较大差异的漂移轨迹点，删除该点并连接其前后序轨迹点
Input：单条轨迹数据 tr={(𝑝0, 𝑡0),(𝑝1, 𝑡1),…,(𝑝𝑛, 𝑡𝑛)}
 
𝑝2的方向与𝑝1、𝑝3的方向差异均大于一定阈值，删除𝑝2
 


Output：tr={(𝑝0, 𝑡0),(𝑝1, 𝑡1),(𝑝3, 𝑡3),…,(𝑝𝑛, 𝑡𝑛)}
 
𝑝0
 
𝑝1
 
𝑝2
 
𝑝3
 
𝑝4
 
𝑝5
 
𝑝6
 
𝑝3的方向为线段𝑝3→𝑝4的方向
 
并连接𝑝1、𝑝3
 

### Speaker notes


### Embedded images
- `ppt/media/image23.png` SHA256=9ba9ba2cf2abeffcc50c5d07adc813c547dbf79b8be568bfd6ae9106421eeac8
- `ppt/media/image22.png` SHA256=480cc9c2598024a18294a79d45f439771bb582f42c8fce4d1967edd35d7d34b8
- `ppt/media/image39.png` SHA256=cb578261943cc378b7de1176da1af1442dee160d675b3e924602d1410c0a79e4
- `ppt/media/image38.png` SHA256=80991fbea410f3ad40717f4c0dc4ea03ec89acc18c92161e1d88da758ce30f48
- `ppt/media/image37.png` SHA256=1769ac517cd72ee4671e6c70a1791a6eb1e1a64e347c66d1e2425b9ca65ccd5c
- `ppt/media/image36.png` SHA256=cf26213fdb53b56f0cc499342f631d7fbaee4ac2087be15355d8fc18d17eaff3
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image42.png` SHA256=597f6c0db8e658b75377fe68b92a53e409207d8a4c6c4aea73f4eb1ff5ce133f
- `ppt/media/image41.png` SHA256=bca5a3cdd6f86ff56d6eb228f549c83ad82e6d19979738f1da306e7e25460bd6
- `ppt/media/image30.png` SHA256=aa61e669952f53910995e9b29c454bea4945c6a01adcb0b76c5546c80c0b5029
- `ppt/media/image29.png` SHA256=fa933038632c00fd260f511e1e504393114d94b2995acaa91dd7196a694249f7
- `ppt/media/image40.png` SHA256=de738cf94b8a368017ed68cc90ee2d5fae9696d30f0d9f5000316070f69406c2
- `ppt/media/image24.png` SHA256=c590d861b684ac84235ffc4e569d94f4f7520d2394a83d9fd57620129bc257bf
- `ppt/media/image25.png` SHA256=c7f53b9a17bef849d411998735a7e85c3da3c6a55d46296d2769805dd01b7125
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 21: ppt/slides/slide21.xml

为什么需要轨迹数据预处理
背景：全国网与车在每小时都会产生大量的轨迹点数据，同时由于交通拥堵，同一车辆在局部区域会产生大量轨迹点。
影响：基于轨迹数据的相关任务效率低下，且精度降低。
解决思路：若删除当前轨迹点对整条轨迹的形态会产生较大影响，则将当前轨迹点视为关键点予以保留。
轨迹点数量过多且存在冗余

局部区域内一周时间收集了接近10万个轨迹点

### Speaker notes


### Embedded images
- `ppt/media/image43.png` SHA256=7e8656f81e456745d56581a160cb85bd18512c3ce0a2c2280d577907e07eccce
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 22: ppt/slides/slide22.xml

为什么需要轨迹数据预处理
解决方法：轨迹压缩

Step1:找到轨迹中离起终点连成线段最远的轨迹点，计算该点到起终点连成线段的距离
Step2: 若该距离大于一定阈值，则说明该点是轨迹tr中的形态关键点，应当保留，将轨迹按该点分割为两条子轨迹，反之则仅保留两个端点，删除其他轨迹点。
Input：单条轨迹数据 tr={(𝑝0, 𝑡0),(𝑝1, 𝑡1),…,(𝑝5, 𝑡5)}
 


Output：tr={(𝑝0, 𝑡0),(𝑝2, 𝑡2),(𝑝3, 𝑡3),(𝑝5, 𝑡5)}
 
计算𝑝3到线段𝑝0→𝑝5的距离
 

道格拉斯普克算法示意图
𝑝0
 
𝑝1
 
𝑝2
 
𝑝3
 
𝑝4
 
𝑝5
 
𝑝0
 
𝑝2
 
𝑝3
 
𝑝5
 
Step3: 重复执行上述步骤直到无法继续压缩。

### Speaker notes


### Embedded images
- `ppt/media/image23.png` SHA256=9ba9ba2cf2abeffcc50c5d07adc813c547dbf79b8be568bfd6ae9106421eeac8
- `ppt/media/image22.png` SHA256=480cc9c2598024a18294a79d45f439771bb582f42c8fce4d1967edd35d7d34b8
- `ppt/media/image47.png` SHA256=eda1c15bddb794ac5c97a01349b517b4a12877282a53f4a1fc7684c3610233dd
- `ppt/media/image46.png` SHA256=1c9cd632e08c33801f0cda52577e8143a0d559b57f400118914a4958628c9138
- `ppt/media/image45.png` SHA256=b2a683ef80d66b0b9d5364d561c6403db08e1c3b0be9ee4d84e98d081fcda957
- `ppt/media/image44.png` SHA256=3d94bec2d4cdfdf2882b83abc91870d459153c36f283c2ae156aafaa0f6afab4
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image29.png` SHA256=fa933038632c00fd260f511e1e504393114d94b2995acaa91dd7196a694249f7
- `ppt/media/image26.png` SHA256=c27293f4c5dfe5db4dadfda5c07a32041cc7d32403ffb8ebe7d12d866bc13b87
- `ppt/media/image24.png` SHA256=c590d861b684ac84235ffc4e569d94f4f7520d2394a83d9fd57620129bc257bf
- `ppt/media/image25.png` SHA256=c7f53b9a17bef849d411998735a7e85c3da3c6a55d46296d2769805dd01b7125
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 23: ppt/slides/slide23.xml

轨迹压缩

### Speaker notes


### Embedded images
- `ppt/media/image49.png` SHA256=e01c0fc33151068e0c307125c0178fc68e69f06295cb0a11b53f66c2fe881754
- `ppt/media/image48.GIF` SHA256=7e9238a44692b82d43f86e1397d81c7555531974f9b444d989ecc6936864d008
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 24: ppt/slides/slide24.xml

轨迹预处理效果评估
分段距离阈值选择
分段处理：将相邻轨迹点中距离超过阈值的点视为噪声点，在噪声点处将轨迹分段。
通过轨迹保存率及先验最大距离计算公式确定分段阈值：
最大距离计算公式：
其中平均采样时间计算为12s左右，骑行速度上界为25km/h，计算得到最大行驶距离约为83m左右，结合图像及实际情况（超速），取分段阈值设置为95m。

### Speaker notes


### Embedded images
- `ppt/media/image52.png` SHA256=3468c3b6f55c761ab7add3e7b0feaed8e7efc4a480948a06b27ed2953b4579a8
- `ppt/media/image51.tiff` SHA256=d14b67d3d86d1d578e938823dd4dd9612dbb8cf7f6810b4e9ac1af82edbc2aad
- `ppt/media/image50.jpeg` SHA256=99a09e9625566bffcbc59e6d13ccf350030600db8ca3b90a6a0b25d7f452396c
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 25: ppt/slides/slide25.xml

轨迹预处理效果评估
分段距离阈值选择
保留比例(%)
（分段后轨迹点数量除以分段前轨迹点数量）

### Speaker notes


### Embedded images
- `ppt/media/image52.png` SHA256=3468c3b6f55c761ab7add3e7b0feaed8e7efc4a480948a06b27ed2953b4579a8
- `ppt/media/image51.tiff` SHA256=d14b67d3d86d1d578e938823dd4dd9612dbb8cf7f6810b4e9ac1af82edbc2aad
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 26: ppt/slides/slide26.xml

作业细则
轨迹数据预处理（必做）：
完成Trajectory_preprocessing.ipynb的空缺部分与实验报告。
设计评价轨迹数据预处理效果的评估指标，需给出设计逻辑以及结果分析。
基于LLM辅助的轨迹数据质量提升智能体系统（选做）：
基于助教开发的系统。


思考与讨论（选做）

作业提交：在10月5日前将.ipynb文件与实验报告压缩至.zip文件格式发送至52285903012@stu.ecnu.edu.cn, 作业命名为 学号_姓名_实验一.zip/.ipynb/.docx/.pdf

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 27: ppt/slides/slide27.xml

Useful Tips
Useful Python Library：
	Shapely：几何对象操作库		Folium：轻量化的地图数据可视化库
	Networkx：图数据操作库		Pytorch: 机器/深度学习框架
	


Useful Links：
	论文数据库（英文）：https://dblp.org/
	论文索引与下载：https://scholar.google.com/


### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 28: ppt/slides/slide28.xml
任务三 · 方法与实现
基于 LLM 的轨迹数据清洗评估
让 LLM 选评估工具、提参数建议，再用定量指标核验建议
四步做法 · 15 个工具 · 四层记忆 · 留出集消融

### Speaker notes
开场。这套方法要把轨迹清洗的参数决策交给 LLM，但它的建议必须能被自动判分。今天讲的是完整做法：怎么组织输入、让 LLM 调哪些工具、参数怎么定、怎么核验它的建议、以及怎么判断这套流程真的有效。


## Slide 29: ppt/slides/slide29.xml
动机
要解决什么问题
① 参数靠猜
清洗参数（比如 DP 容差、速度阈值）通常是手工试出来的，换个数据集就失效。
② 没法判分
让 LLM 给个参数很容易，但「它提得对不对」没有量化判据，只能靠人看。
③ 成本不可行
11386 条轨迹，每条都调 LLM 不现实，需要让结果可以复用。
本课要讲的就是怎么同时解决②和③：把 LLM 的建议变成可自动判分的数字，并让结果可以复用。
2

### Speaker notes
这是动机页。核心是第二点：没法判分。做工程的人最容易忽略这点，结果做出来的东西只能演示不能评价。建议点明：本课所有设计都是为了让第三点（成本）和第二点（判分）同时成立。


## Slide 30: ppt/slides/slide30.xml
方法总览
整体做法：四步
第一步

把数据变成

LLM 能读的输入

诊断卡 + 句柄
第二步

让 LLM 决定

用什么工具、提什么参数

函数调用
第三步

参数不靠猜

物理先验定区间

确定性代码给边界
第四步

核验它的建议

跟确定性搜索最优比

regret 判分
LLM 只出现在第二步。第一步用确定性统计替代它的语感，第三、四步用确定性搜索替代人的判断。
这样做的结果：LLM 的建议好坏变成一个数字，而不是一段需要人读的解释。
同时因为第三、四步是确定性的，它们不消耗 API 调用，成本是可控的。
3

### Speaker notes
这是方法论总览，后面每一页都在展开其中一步。建议强调第一步是替代 LLM 的语感，第三步是替代人的判断。LLM 只出现在第二步。


## Slide 31: ppt/slides/slide31.xml
第一步：把数据变成 LLM 能读的输入
117 万个点不可能进上下文。
所以只给两样东西：
句柄字符串，例如 246#0@v3
一张诊断卡，只含标量统计
诊断卡约 400 到 600 字节。11386 条全量也只有几 MB。
每次清洗或压缩产生新句柄并记录血缘，过程可完整重放。
诊断卡里最有用的是 regime 和时间轴质量，它们直接决定该用哪套参数
// 诊断卡（无任何坐标）

seg_id:     246#0@v3

n_points:   106

regime:     moving

timeline:   ok

dt_median:  10.0

dt_p95:     20.0

dup_ratio:  0.019

speed_p99:  100.77

anomalies:  {

  dt_artifact: 4,

  space_jump:  9 }

// 没有 coords 字段
4

### Speaker notes
这一步的关键是纪律。117 万个点不可能进上下文，所以只给标量和句柄。诊断卡里最有用的是 regime 和时间轴质量，因为它们直接决定该用哪套参数。


## Slide 32: ppt/slides/slide32.xml
关键前提
为什么要先分类型

63%
静止轨迹

17%
混合

20%
行驶轨迹
200 条抽样的轨迹类型分布
静止与行驶是两个完全不同的群体。
静止轨迹：位移中位 42 米，重复点可占 90%，中位速度 0.1 m/s。
行驶轨迹：位移数公里至 20 公里，重复点通常低于 10%。
对这两类用同一套阈值，不是效果差一点，而是对其中一半数据完全失效。
所以诊断卡把类型放在最前面，LLM 一眼就能看到该换参数。
占比来自 200 条抽样的实测统计
5

### Speaker notes
这一页解释为什么不能对全部数据用一套参数。实测数据是两个截然不同的群体，混在一起做参数推荐一定失败。这也是让 LLM 看诊断卡而不是看坐标的原因。


## Slide 33: ppt/slides/slide33.xml
做法
第二步：给 LLM 的工具箱
类别
工具
作用
查数据
profile · detect_anomalies · evaluate · compare_handles
返回标量统计，不含坐标
改数据
split · clean · simplify · apply_road_constraint
产生新句柄
做实验
run_search · find_knee · suggest_param_range
扫描参数、取拐点
查经验
query_memory · query_playbook
相似案例 + 人类笔记
出图
render
叠加图 / 异常分布 / 热力图
刻意不给
write_memory · write_playbook
LLM 无权写记忆
为什么故意不给写记忆的工具：如果 LLM 能直接写，一次幻觉就会被后续检索不断放大，而且很难发现。记忆的写入权只交给核验通过的确定性代码。
所有工具都是确定性函数，没有随机性、不联网、不调用 LLM
6

### Speaker notes
讲工具分类。重点是刻意不提供写记忆的工具，这条规则让记忆不会被幻觉污染。另外要说明工具返回的都是标量统计，不是坐标。


## Slide 34: ppt/slides/slide34.xml
做法
第三步：参数怎么定
① 物理先验定区间
9 个参数各有合法区间
由数据分布或物理量反推
确定性代码
② LLM 提起点与方向
给出参数值 + 预期效果
强制结构化输出
LLM
③ 有界搜索精调
坐标下降 + 拐点
产出 ground truth
确定性代码
关键：LLM 不是优化器，它只给起点和方向。
dp_tolerance 区间 [0.5, 30] 米，上限约等于 GPS 定位精度。
dt_threshold 区间 [15, 180] 秒，下界保住正常的 20 秒采样。
dist_threshold 由 Δt × 限速 × 安全系数推导，不由位移分布推导。
「预期效果」这一栏是白送的评分抓手。LLM 必须预测每个参数的升降方向，核验时只需比对符号，就能零成本算出方向准确率。
7

### Speaker notes
回答参数怎么调这个核心问题。LLM 只给起点和方向，不给最终值。这是本方法与传统自动调参最不同的地方，也是它能被自动判分的原因。


## Slide 35: ppt/slides/slide35.xml
核心
第四步：怎么判断 LLM 提得对不对
regret = 搜索最优分 − LLM 提议分
它需要 ground truth。所以在同一预算内跑一次确定性搜索作为标尺。
实测一条：提议 0.6008、基线 0.6330、最优 0.6366，得 regret 0.0358。
另外两个零成本判据：
方向准确率：预测的升降符号与实测是否一致
约束满足率：提议是否落在物理先验区间内
口径
触发条件
怎么读
归一化
最优与基线差距充足
丢掉了多少比例的可得收益
绝对
最优与基线差距过小
分母趋零会放大微小差距
不适用
轨迹过短（< 200 米）
压缩率在该尺度无物理含义
三种口径必须显式标注。混用会让结论完全反过来：headroom 只有 0.021 时，一个与基线持平的提议会被算成 regret 1.0。
这就是「用定量指标核验建议」的具体落地
8

### Speaker notes
核心页，建议讲慢。regret 需要 ground truth，所以必须跑一次确定性搜索。三种口径一定要讲清楚，否则会得出错误结论。方向准确率是零成本的额外判据，值得强调。


## Slide 36: ppt/slides/slide36.xml
做法
记忆怎么用：让流程越跑越省
层
存什么
谁写
怎么用
工作记忆
当前轨迹的诊断卡与已试参数
agent
单条轨迹内
情景记忆
全量（诊断 → 参数 → 实测指标）
核验器
积累原始经验
程序记忆
诊断签名 → 参数区间
核验器
12 维特征 kNN 检索
人类知识
结论 + 证据 + 反例
人
只读，给 LLM 因果解释
机器算出来的参数区间（程序记忆）和人写的因果解释（人类知识）不重复：前者给数字锚点，后者给物理直觉。
成本含义：跑少数轨迹积累经验，其余轨迹直接查区间清洗，零 LLM 调用。这是 11386 条能落地的关键。
安全边界：agent 对人类知识库只有读权限。它的任何 bug 都不可能损坏知识库。
9

### Speaker notes
讲清楚为什么要分层。L2 是机器算出来的统计，L3 是人写的解释，两者不冲突。注意最后一行的成本含义：跑少数、复用多数，这是 11386 条能落地的关键。


## Slide 37: ppt/slides/slide37.xml
验证方法
消融实验：怎么证明这套流程有效
四种模式必须结构性不同
llm-only：只有 LLM，没有实测依据
search-only：只有确定性搜索，不含任何 LLM 调用
llm+search：加上实测依据
llm+memory+search：再加上历史经验
两个必须避开的陷阱
信息泄漏：在评测轨迹上边跑边攒记忆，agent 会把这条轨迹自己的上次结果检索回来。等于考试时把答案摆桌上。
标签造假：search-only 若仍调用 LLM，与含 LLM 的模式就不可比。所以它必须真的不调用，并有测试断言轮次为 0。
做法：先在示范集上积累记忆，再在完全不重叠的留出集上评测。评测阶段只读不写。
10

### Speaker notes
方法论页。两个陷阱都会让结论完全相反，而且都很隐蔽。信息泄漏尤其容易犯，因为它在单条轨迹上看不出任何异常。


## Slide 38: ppt/slides/slide38.xml
结果
实测结果：记忆层没有带来可测增益

50%
llm-only

25%
search-only

41.7%
llm+search

41.7%
llm+
memory
+search
超基线率（提议显著优于基线的比例）
三种含 LLM 模式的提议分逐位相同。
根因已定位到具体层面：
示范集准入的 5 条里，4 条是静止、1 条混合。
行驶类轨迹在记忆里一条已验证案例都没有。
所以 4 条行驶类留出样本检索到的可用区间数是 0。
结论：这是示范集太小造成的数据饥饿，不是方法失败。
11

### Speaker notes
必须如实讲。三种含 LLM 模式的得分完全相同。根因是 moving 类轨迹在记忆里一条已验证案例都没有，所以检索到的可用信息是零。这是数据饥饿，不是方法失败。


## Slide 39: ppt/slides/slide39.xml
实践提醒
六个被数据推翻的假设
问题
实测症状
修法
距离用墨卡托
31°N 系统性放大 17%，容差预算凭空偏 17%
换局部等距投影
Hausdorff 口径错
顶点集算法给 548 米，真实值 4.77 米
改点到折线
DP 偏差估计错
容差 2 米时报出 8349 米
从递归结构取精确界
在噪声上算航向
单条静止轨迹假掉头 37 个
加 10 米噪声地板
漂移用绝对偏移
误判 50% 的正常行驶点
改无量纲曲率
毛刺用位移法识别
一处毛刺污染两个位置，真毛刺抓不到
改相对插值位置偏差
这些坑的共同点：代码都不会报错，只会让结论错。所以每条都写了回归测试。
12

### Speaker notes
这页对做过实际数据处理的人最有价值。挑两三个讲透即可，比如墨卡托放大 17% 和 Hausdorff 的 548 米对 4.77 米。这些坑都不会让代码报错，只会让结论错。


## Slide 40: ppt/slides/slide40.xml
现状
现在能跑到什么程度
可以直接用
离线模式可完整跑通全流程
接真实模型只需设一个环境变量
参数判分与记忆准入已可用
六类报告图自动产出
还没验证
记忆增益（需扩大示范集）
真实 LLM 的消融（未跑过）
路网约束（仅有接口）
全量 11386 条（未跑）
离线 provider 每次给出同一个拐点，天然抹平了模式差异。不接真实模型，消融表就没有信息量。
13

### Speaker notes
如实交代边界。左侧可直接用，右侧是还没验证的部分。不要把未验证的说成已验证。


## Slide 41: ppt/slides/slide41.xml
下一步
怎么接着做 （怎么做更实用，更强大的智能体）
你认为还能怎么做呢？
14
T-Assess: An Efficient Data Quality Assessment System Tailored for Trajectory Data

### Speaker notes
三条按收益排序。第一条最紧，如果不解决，后面两条得出的结论都不可信。


## Slide 42: ppt/slides/slide42.xml

思考与讨论
轨迹分段、轨迹去噪、轨迹简化三个步骤可不可以调换顺序？

### Speaker notes


### Embedded images
- `ppt/media/image9.png` SHA256=1755a85c5f146fe93ab327e267a72fad8691c868a50dd3d7b90776fa6b5adba0
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image8.jpeg` SHA256=fd0d124b3f31d8d270fc219400872a6b05255c4530633b4cf7518561600cc3eb

## Slide 43: ppt/slides/slide43.xml

谢谢！


Email：52285903012@stu.ecnu.edu.cn 

### Speaker notes


### Embedded images
- `ppt/media/image5.png` SHA256=f3fd0305b0d41ae96a8589425f06aaed96c56ef727d13e046338ec55d17a128e
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image6.png` SHA256=7b4cf3aaa8948c9858dd7ebfbf9cdec6e3a147de2ad2c251bd09e029b785e4e1
- `[external/missing image relationship; source target withheld from public extract]` SHA256=unavailable
- `ppt/media/image4.jpeg` SHA256=52ee35a00838544ca89cd26635138deb108bc87b7e5b9b9446c714763bd9990a
