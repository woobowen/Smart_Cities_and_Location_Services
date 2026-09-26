# Notebook extraction: task1/作业/作业/作业1轨迹数据预处理.ipynb
Source SHA256: 8601d1dfecaef062fef553992cc9774d3a0eb551751c70536f5b52f1343b158a
Classification: teacher/starter source; all saved execution counts and outputs are HISTORICAL.
Notebook metadata: {"kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"}, "language_info": {"codemirror_mode": {"name": "ipython", "version": 3}, "file_extension": ".py", "mimetype": "text/x-python", "name": "python", "nbconvert_exporter": "python", "pygments_lexer": "ipython3", "version": "3.10.9"}}

## Cell 0 (code), execution_count=1
Cell metadata: {"tags": []}
```python
#导包：公共数据包
import csv
import pandas as pd
import time
import json
import numpy as np
from shapely.geometry import LineString
import os
import datetime
#导包：自有包
from utils import util as util
from douglas_peucker import DouglasPeuker
from utils import visualization as visual
```
## Cell 1 (code), execution_count=2
Cell metadata: {"tags": []}
```python
# 需要调整的阈值
LIMIT_LENGTH = 65  # 轨迹长度小于该值的将被过滤掉
LIMIT_POINT = 5  # 轨迹点数小于该值的将被过滤掉
LIMIT_DT = 30  # 时间戳间隔大于该值的将被分段 3 * 平均采样间隔（10s）
LIMIT_DISTANCE = 400  # 距离大于该值的将被分段 2 * 平均采样间隔（10s）* 城市限速（20m/s）
LIMIT_DIRECTION = 35  # 方向变换大于该值的将去噪
DP_THRESHOLD = 5  # 道格拉斯-普克 阈值
```
## Cell 2 (code), execution_count=3
Cell metadata: {"tags": []}
```python
# 调用道格拉斯-普克算法，减少轨迹点索引，轨迹抽稀
def get_reduction_traj_index(coordinates):
    traj_mercator = util.transform_points_wgs84_to_mercator(coordinates)
    result_index = []
    d = DouglasPeuker(DP_THRESHOLD)
    d.reduction(traj_mercator)
    temp_list = d.qualify_list
    for i, item in enumerate(traj_mercator):
        if item in temp_list:
            result_index.append(i)
    return result_index  # 抽稀后的坐标点索引

# 计算速度和方向
def calculate_speed_and_dir(traj):
    result = dict()
    for key, value in traj.items():
        directions = util.get_direction(value[1])
        velocities = util.get_velocity(value[1], value[0])
        result[key] = [value[0], value[1], velocities, directions]
    return result
```
## Cell 3 (markdown), execution_count=None
Cell metadata: {}
```text
## 1.完成轨迹分段代码实现
```
## Cell 4 (code), execution_count=4
Cell metadata: {"tags": []}
```python
# 轨迹分段 
def split_traj(traj):  # traj {'id':[[时间戳],[坐标点]]}
    res = {}
    # 待填充
    return res
```
## Cell 5 (markdown), execution_count=None
Cell metadata: {}
```text
## 2.完成轨迹去噪代码实现
```
## Cell 6 (code), execution_count=5
Cell metadata: {"tags": []}
```python
# 轨迹去噪
def denoise_traj(traj):  # traj {'id':[[时间戳],[坐标点],[方向],[速度]]}
    res = {}
    # 待填充
    return res
```
## Cell 7 (markdown), execution_count=None
Cell metadata: {}
```text
## 3.完成轨迹简化代码实现
```
## Cell 8 (code), execution_count=6
Cell metadata: {"tags": []}
```python
## 3.完成轨迹简化代码实现# 轨迹去噪
def simplify_traj(traj):  # traj {'id':[[时间戳],[坐标点],[方向],[速度]]}
    res = {}
    # 待填充
    return res
```
## Cell 9 (markdown), execution_count=None
Cell metadata: {}
```text
## 4.主函数
```
## Cell 10 (code), execution_count=7
Cell metadata: {}
```python
traj_dict = json.load(open('traj_dict.json'))
tra_split = split_traj(traj_dict)
tra_denoise = denoise_traj(tra_split)
tra_simplify = simplify_traj(tra_denoise)
```
## Cell 11 (code), execution_count=8
Cell metadata: {"scrolled": false}
```python
traj_dict['0']
```
### Output 0: execute_result
execution_count=8
text/plain:
```
[[1523293209,
  1523293229,
  1523293240,
  1523293249,
  1523293259,
  1523293270,
  1523293289,
  1523293310,
  1523293311,
  1523293319,
  1523293329,
  1523293349,
  1523293359,
  1523293369,
  1523293379,
  1523293389,
  1523293409,
  1523293419,
  1523293429,
  1523293439,
  1523293449,
  1523293469,
  1523293479,
  1523293489,
  1523293499,
  1523293509,
  1523293529,
  1523293539,
  1523293549,
  1523293559,
  1523293569,
  1523293589,
  1523293599,
  1523293609,
  1523293619,
  1523293629,
  1523293649,
  1523293659,
  1523293669,
  1523293679,
  1523293689,
  1523293709,
  1523293719,
  1523293729,
  1523293739,
  1523293749,
  1523293769,
  1523293779,
  1523293789,
  1523293799,
  1523293809,
  1523293829,
  1523293839,
  1523293849,
  1523293859,
  1523293869,
  1523293889,
  1523293899,
  1523293909,
  1523293919,
  1523293929,
  1523293949,
  1523293959,
  1523293969,
  1523293979,
  1523293989,
  1523294009,
  1523294019,
  1523294029,
  1523294039,
  1523294049,
  1523294069,
  1523294079,
  1523294089,
  1523294099,
  1523294109,
  1523294129,
  1523294139,
  1523294149,
  1523294159,
  1523294169,
  1523294189,
  1523294199,
  1523294209,
  1523294219,
  1523294229,
  1523294249,
  1523294259,
  1523294269,
  1523294279,
  1523294289,
  1523294309,
  1523294319,
  1523294329,
  1523294339,
  1523294350,
  1523294369,
  1523294379,
  1523294395],
 [[121.472353, 31.31464],
  [121.472353, 31.31464],
  [121.472357, 31.314633],
  [121.472357, 31.314633],
  [121.472357, 31.314633],
  [121.472357, 31.314633],
  [121.472357, 31.314633],
  [121.47236200000002, 31.314627],
  [121.47236200000002, 31.314627],
  [121.47236200000002, 31.314627],
  [121.47236200000002, 31.314627],
  [121.47236200000002, 31.314627],
  [121.472367, 31.314623],
  [121.472367, 31.314623],
  [121.472367, 31.314623],
  [121.472367, 31.314623],
  [121.472367, 31.314623],
  [121.472372, 31.314618],
  [121.472372, 31.314618],
  [121.472372, 31.314618],
  [121.472372, 31.314618],
  [121.472372, 31.314618],
  [121.472378, 31.314613],
  [121.472378, 31.314613],
  [121.472378, 31.314613],
  [121.472378, 31.314613],
  [121.472378, 31.314613],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.47239, 31.314608000000003],
  [121.47239, 31.314608000000003],
  [121.47239, 31.314608000000003],
  [121.47239, 31.314608000000003],
  [121.47239, 31.314608000000003],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472388, 31.31461],
  [121.472387, 31.31461],
  [121.472387, 31.31461],
  [121.472387, 31.31461],
  [121.472387, 31.31461],
  [121.472387, 31.31461],
  [121.472383, 31.31461],
  [121.472383, 31.31461],
  [121.472383, 31.31461],
  [121.472383, 31.31461],
  [121.472383, 31.31461],
  [121.472388, 31.314605],
  [121.472388, 31.314605],
  [121.472388, 31.314605],
  [121.472388, 31.314605],
  [121.472388, 31.314605],
  [121.472395, 31.314598],
  [121.472395, 31.314598],
  [121.472395, 31.314598],
  [121.472395, 31.314598],
  [121.472395, 31.314598],
  [121.472395, 31.314595],
  [121.472395, 31.314595],
  [121.472395, 31.314595],
  [121.472395, 31.314595],
  [121.472395, 31.314595],
  [121.472395, 31.314593],
  [121.472395, 31.314593],
  [121.472395, 31.314593],
  [121.472395, 31.314593],
  [121.472395, 31.314593],
  [121.472392, 31.314593],
  [121.472392, 31.314593],
  [121.472392, 31.314593],
  [121.472392, 31.314593],
  [121.472392, 31.314593],
  [121.47238, 31.314593],
  [121.47238, 31.314593],
  [121.47238, 31.314593],
  [121.47238, 31.314593],
  [121.47238, 31.314593],
  [121.47237, 31.314592],
  [121.47237, 31.314592],
  [121.47237, 31.314592],
  [121.47237, 31.314592],
  [121.47237, 31.314592],
  [121.472363, 31.314593],
  [121.472363, 31.314593],
  [121.472363, 31.314593],
  [121.472363, 31.314593],
  [121.472363, 31.314593],
  [121.472355, 31.314593],
  [121.472355, 31.314593],
  [121.472355, 31.314593],
  [121.472355, 31.314593],
  [121.472355, 31.314593],
  [121.472355, 31.314595],
  [121.472355, 31.314595]]]
```
metadata:
```
{}
```
## Cell 12 (markdown), execution_count=None
Cell metadata: {}
```text
##### 5.轨迹分段超参数实验（提示：距离、时间阈值对分段后剩余轨迹点数量的影响）选做
```
## Cell 13 (code), execution_count=None
Cell metadata: {}
```python

```
## Cell 14 (markdown), execution_count=None
Cell metadata: {}
```text
##### 6.轨迹去噪超参数实验 选做
```
## Cell 15 (code), execution_count=None
Cell metadata: {}
```python

```
## Cell 16 (markdown), execution_count=None
Cell metadata: {}
```text
##### 7.轨迹简化超参数实验 选做
```
## Cell 17 (code), execution_count=None
Cell metadata: {}
```python

```
## Cell 18 (code), execution_count=10
Cell metadata: {}
```python
import numpy as np
import matplotlib.pyplot as plt

def douglas_peucker(points, epsilon):
    """
    Douglas-Peucker 算法
    :param points: 点列表，shape (n, 2)
    :param epsilon: 阈值，越大越简化
    :return: 简化后的点列表
    """
    points = np.array(points)  # ✅ 强制转 array

    # 找到离首尾连线最远的点
    start_point = points[0]
    end_point = points[-1]
    
    # 向量
    vec = end_point - start_point
    line_len = np.linalg.norm(vec)
    
    if line_len == 0:
        return [start_point]
    
    # 单位向量
    unit_vec = vec / line_len
    
    # 计算每个点到线段的距离
    seg_vec = points - start_point
    proj_lengths = np.dot(seg_vec, unit_vec)
    proj_points = start_point + proj_lengths[:, np.newaxis] * unit_vec
    
    distances = np.linalg.norm(points - proj_points, axis=1)
    max_dist = np.max(distances)
    max_idx = np.argmax(distances)
    
    if max_dist > epsilon:
        # 递归处理两段
        left = douglas_peucker(points[:max_idx+1], epsilon)
        right = douglas_peucker(points[max_idx:], epsilon)
        # 合并，去重中间点
        return left[:-1] + right
    else:
        return [start_point, end_point]

# 使用示例
np.random.seed(42)
x = np.linspace(0, 10, 100)
y = np.sin(x) + 0.1 * np.random.randn(100)
points = np.column_stack((x, y))

simplified = douglas_peucker(points.tolist(), epsilon=0.2)
simplified = np.array(simplified)

# 可视化
plt.figure(figsize=(10, 5))
plt.plot(points[:, 0], points[:, 1], 'b-', label='orig', alpha=0.6)
plt.plot(simplified[:, 0], simplified[:, 1], 'ro-', label=f'simply ({len(simplified)} point)')
plt.legend()
plt.title('Douglas-Peucker ')
plt.grid(True)
plt.show()
```
### Output 0: stream
execution_count=None
name:
```
stderr
```
text:
```
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 25163 (\N{CJK UNIFIED IDEOGRAPH-624B}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 21160 (\N{CJK UNIFIED IDEOGRAPH-52A8}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 23454 (\N{CJK UNIFIED IDEOGRAPH-5B9E}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 29616 (\N{CJK UNIFIED IDEOGRAPH-73B0}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 21407 (\N{CJK UNIFIED IDEOGRAPH-539F}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 22987 (\N{CJK UNIFIED IDEOGRAPH-59CB}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 31616 (\N{CJK UNIFIED IDEOGRAPH-7B80}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 21270 (\N{CJK UNIFIED IDEOGRAPH-5316}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)
D:\anaconda\lib\site-packages\IPython\core\pylabtools.py:152: UserWarning: Glyph 28857 (\N{CJK UNIFIED IDEOGRAPH-70B9}) missing from current font.
  fig.canvas.print_figure(bytes_io, **kw)

```
### Output 1: display_data
execution_count=None
image/png: binary/base64 payload omitted from readable copy; characters=60729, SHA256=fd8450ad3d7288fe4e48d688b55d802946aefebf3a8e6693cc9e480f50036b28; original remains in source notebook.
text/plain:
```
<Figure size 1000x500 with 1 Axes>
```
metadata:
```
{}
```