## Cell 0 (markdown)

# 实验三 网约车派单进阶：多目标进化优化 & 强化学习派单

实验二里我们用贪心（TBG）和批次匹配（KM）解决了"最小化接驾延迟"的单目标派单问题。真实平台面临两个更难的问题：

1. **多个目标互相冲突**：平台想多赚钱（优先派长途单），乘客想少等车（优先派近的司机），两者不能同时最优 → 需要找**帕累托前沿**。
2. **今天的派单会影响明天的供给**：把司机派往偏远区域，他送完客后可能长时间接不到单 → 需要考虑**长期价值**。

| 部分 | 问题 | 方法 | 你需要做的 |
|---|---|---|---|
| Part A | 同时**最大化平台总收入**、**最小化总接驾距离** | NSGA-II / NSGA-III | 代码已全部给出：运行、调参、分析帕累托前沿 |
| Part B | 派单时考虑区域的长期价值，最大化全天收入 | Q-learning + KM（Q-KM） | **完成 TODO 1~3**，训练并与基线对比 |

运行环境：Python ≥ 3.8，`numpy / pandas / scipy / matplotlib`。数据放在 `foursquare/dataset_TSMC2014_NYC.csv`。
全部运行约需 5~10 分钟（主要耗时在 NSGA 与 Q-learning 训练）。

## Cell 1 (code)

import math
import os
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment   # KM（匈牙利）算法，求最小权完美匹配

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "PingFang SC", "SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DATA_PATH = "foursquare/dataset_TSMC2014_NYC.csv"
FIG_DIR = "figures_exp3"              # 实验图表输出目录
os.makedirs(FIG_DIR, exist_ok=True)
SEED = 2024

# ---- 研究区域：纽约主城区（曼哈顿 + 布鲁克林 / 皇后区西部）----
LAT_MIN, LAT_MAX = 40.60, 40.88
LON_MIN, LON_MAX = -74.05, -73.75
KM_PER_LAT = 111.0                                   # 1° 纬度 ≈ 111 km
KM_PER_LON = 111.0 * math.cos(math.radians(40.74))   # 1° 经度 ≈ 84 km
W_KM = (LON_MAX - LON_MIN) * KM_PER_LON              # 区域东西宽 ≈ 25 km
H_KM = (LAT_MAX - LAT_MIN) * KM_PER_LAT              # 区域南北高 ≈ 31 km

# ---- 计价（与实验二仿真器一致）----
BASE_FARE = 5.0      # 起步价（元）
PER_KM = 2.0         # 每公里单价（元/km）
PICKUP_RADIUS = 3.0  # 派单半径：司机与上车点曼哈顿距离不超过 3 km 才能派

## Cell 2 (markdown)

## 0. 数据准备：从签到数据构造"订单"

Foursquare 数据只有用户签到，没有真实打车记录。我们做一个合理假设：
**同一用户同一天内相邻两次签到，若间隔 10~180 分钟且距离 ≥ 1 km，就视为一次出行（一个订单）**。
前一次签到地点 = 上车点，后一次签到地点 = 下车点，前一次签到时间 = 下单时间。

经纬度投影到以 (LAT_MIN, LON_MIN) 为原点的平面坐标（单位 km），距离采用曼哈顿距离（近似街区路网）。
按日期切分：前 70% 的日期作为**历史数据（训练）**，后 30% 作为**未来数据（测试）**。

## Cell 3 (code)

def to_xy(lat, lon):
    """经纬度 -> 平面坐标 (km)"""
    return (lon - LON_MIN) * KM_PER_LON, (lat - LAT_MIN) * KM_PER_LAT


def load_checkins(path=DATA_PATH):
    df = pd.read_csv(path, encoding="latin-1")
    utc = pd.to_datetime(df["utcTimestamp"], format="%a %b %d %H:%M:%S +0000 %Y")
    df["local"] = utc + pd.to_timedelta(df["timezoneOffset"], unit="m")
    inside = df.latitude.between(LAT_MIN, LAT_MAX) & df.longitude.between(LON_MIN, LON_MAX)
    df = df[inside].copy()
    df["x"], df["y"] = to_xy(df.latitude.values, df.longitude.values)
    df["minute"] = df["local"].dt.hour * 60 + df["local"].dt.minute
    return df.sort_values(["userId", "local"]).reset_index(drop=True)


def build_trips(ck, min_gap=10, max_gap=180, min_km=1.0):
    """相邻两次签到 -> 一次出行"""
    prev = ck.groupby("userId")[["x", "y", "local", "minute"]].shift()
    gap = (ck["local"] - prev["local"]).dt.total_seconds() / 60
    km = (ck["x"] - prev["x"]).abs() + (ck["y"] - prev["y"]).abs()
    ok = (ck["local"].dt.date == prev["local"].dt.date) & gap.between(min_gap, max_gap) & (km >= min_km)
    trips = pd.DataFrame({
        "date": prev.loc[ok, "local"].dt.date.values,
        "minute": prev.loc[ok, "minute"].values.astype(int),
        "ox": prev.loc[ok, "x"].values, "oy": prev.loc[ok, "y"].values,
        "dx": ck.loc[ok, "x"].values, "dy": ck.loc[ok, "y"].values,
    })
    trips["trip_km"] = (trips.ox - trips.dx).abs() + (trips.oy - trips.dy).abs()
    trips["fare"] = BASE_FARE + PER_KM * trips["trip_km"]   # 收入 ∝ 送客距离
    return trips.reset_index(drop=True)


ck = load_checkins()
trips = build_trips(ck)
dates = np.sort(trips["date"].unique())
split_date = dates[int(len(dates) * 0.7)]
trips_train = trips[trips.date < split_date].reset_index(drop=True)
trips_test = trips[trips.date >= split_date].reset_index(drop=True)
print(f"签到 {len(ck)} 条，构造订单 {len(trips)} 个，覆盖 {len(dates)} 天")
print(f"训练集 {len(trips_train)} 单（{dates[0]} ~ {split_date}），测试集 {len(trips_test)} 单")
print(trips[["trip_km", "fare"]].describe().round(2))

## Cell 4 (code)

fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
hourly = trips.groupby(trips.minute // 60).size()
axes[0].bar(hourly.index, hourly.values, color="#9F3A3D")
axes[0].set(title="订单量的时间分布", xlabel="小时", ylabel="订单数")
axes[1].hexbin(trips.ox, trips.oy, gridsize=45, bins="log", cmap="Reds")
axes[1].set(title="上车点空间分布（log 密度）", xlabel="x / km", ylabel="y / km", aspect="equal")
axes[2].hist(trips.trip_km, bins=50, color="#4c78a8")
axes[2].set(title="送客距离分布", xlabel="km", ylabel="订单数")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/data_overview.png", dpi=200)
plt.show()

## Cell 5 (markdown)

# Part A 多目标派单：NSGA-II / NSGA-III

## A.1 问题建模

某一时刻（一个批次）平台手里有 $n$ 个空闲司机、$m$ 个待派订单，且**司机少于订单**（高峰期常态）。决策变量 $x_{ij}\in\{0,1\}$ 表示司机 $i$ 是否接订单 $j$：

$$\max\ f_1=\sum_{i,j}\text{fare}_j\,x_{ij}\qquad \min\ f_2=\sum_{i,j}d^{\text{pick}}_{ij}\,x_{ij}$$
$$\text{s.t. } \sum_j x_{ij}\le 1,\ \ \sum_i x_{ij}\le 1,\ \ x_{ij}=0 \text{ if } d^{\text{pick}}_{ij}>R$$

两个目标冲突：长途单价高但上车点不一定离司机近；派更多单收入高，但总接驾距离也更大。
不存在同时最优的解，只能求**帕累托最优解集**（Pareto set），它在目标空间中的像就是**帕累托前沿**。

**编码**：长度为 $m$ 的整数向量，第 $j$ 位 $g_j\in\{0,1,\dots,K\}$：$g_j=0$ 表示订单 $j$ 本批次不派，$g_j=k$ 表示派给第 $k$ 近的候选司机。
**解码修复**：若两个订单抢同一个司机，后者顺延到下一个候选；都被占则不派。这样任意基因都能解码成**可行**匹配。

进化算法统一**最小化**，所以目标向量写成 $F=(-f_1,\ f_2)$。

## Cell 6 (code)

def make_batch(trip_pool, hour, n_orders=80, n_drivers=40, seed=0):
    """从历史订单中抽取某小时的一个派单批次；司机分布在签到热点附近（模拟巡游出租车）"""
    rng = np.random.default_rng(seed)
    pool = trip_pool[trip_pool.minute // 60 == hour]
    od = pool.sample(n_orders, replace=len(pool) < n_orders, random_state=seed)
    hot = ck[ck.minute // 60 == hour][["x", "y"]].values
    drv = hot[rng.integers(0, len(hot), n_drivers)] + rng.normal(0, 1.0, (n_drivers, 2))
    o_xy = od[["ox", "oy"]].values
    pickup = np.abs(drv[:, None, :] - o_xy[None, :, :]).sum(-1)   # (n, m) 接驾曼哈顿距离
    return dict(drv=drv, o_xy=o_xy, d_xy=od[["dx", "dy"]].values,
                fare=od["fare"].values, pickup=pickup)


class DispatchProblem:
    """把一个批次包装成多目标优化问题：基因 -> 匹配 -> 目标向量"""

    def __init__(self, batch, K=6, radius=PICKUP_RADIUS, n_obj=2):
        self.fare, self.pickup = batch["fare"], batch["pickup"]
        self.n_drivers, self.n_var = self.pickup.shape
        self.K, self.n_obj = K, n_obj
        order_view = self.pickup.T                              # (m, n)
        cand = np.argsort(order_view, axis=1)[:, :K]           # 每个订单最近的 K 个司机
        ok = np.take_along_axis(order_view, cand, 1) <= radius
        self.cand = np.where(ok, cand, -1)                      # -1 表示该候选不可行
        self.n_cand = ok.sum(1)                                 # 每个订单的可行候选数

    def decode(self, gene):
        """基因 -> [(driver, order), ...]，冲突时顺延到下一个候选司机"""
        used = np.zeros(self.n_drivers, bool)
        pairs = []
        for j, g in enumerate(gene):
            c = self.n_cand[j]
            if g == 0 or c == 0:
                continue
            for s in range(c):
                d = self.cand[j, (g - 1 + s) % c]
                if not used[d]:
                    used[d] = True
                    pairs.append((d, j))
                    break
        return pairs

    def evaluate_one(self, gene):
        pairs = self.decode(gene)
        if not pairs:
            return np.zeros(self.n_obj)
        d, j = np.array(pairs).T
        f = [-self.fare[j].sum(), self.pickup[d, j].sum()]
        if self.n_obj == 3:
            f.append(-len(pairs))                               # 第三目标：最大化服务订单数
        return np.array(f, float)

    def evaluate(self, pop):
        return np.array([self.evaluate_one(g) for g in pop])

    def random_population(self, size, rng):
        pop = rng.integers(0, self.K + 1, (size, self.n_var))
        pop[0] = 1                                              # 种子个体：全部派给最近司机
        pop[1] = 0                                              # 种子个体：全部不派（f=0 的端点）
        return pop


batch = make_batch(trips_train, hour=18, seed=SEED)
prob = DispatchProblem(batch)
print("司机数", prob.n_drivers, "订单数", prob.n_var,
      "| 无可行司机的订单", int((prob.n_cand == 0).sum()),
      "| 平均可行候选", prob.n_cand.mean().round(2))

## Cell 7 (markdown)

## A.2 NSGA-II

NSGA-II（Deb, 2002）三个核心组件：

1. **快速非支配排序**：$a$ 支配 $b$ ⇔ $a$ 在所有目标上不差于 $b$ 且至少一个严格更好。把种群分层 $F_1, F_2,\dots$，$F_1$ 是当前帕累托前沿。
2. **拥挤距离**：同一层内，个体在每个目标上相邻两点的归一化距离之和。距离大 = 周围稀疏，优先保留，以维持多样性。边界点距离为 ∞。
3. **精英保留 (μ+λ)**：父代与子代合并成 $2N$ 个个体，按 (层号小, 拥挤距离大) 选出 $N$ 个进入下一代。

遗传算子：二元锦标赛选择、均匀交叉、随机重置变异（每位以 $1/m$ 概率重置）。

## Cell 8 (code)

def fast_non_dominated_sort(F):
    """返回 rank 数组（0 = 第一层前沿）"""
    N = len(F)
    le = (F[:, None, :] <= F[None, :, :]).all(-1)
    lt = (F[:, None, :] < F[None, :, :]).any(-1)
    dom = le & lt                          # dom[a, b] = a 支配 b
    n_dominated_by = dom.sum(0)            # 每个个体被多少个体支配
    rank = np.full(N, -1)
    current = np.where(n_dominated_by == 0)[0]
    r = 0
    while len(current):
        rank[current] = r
        n_dominated_by = n_dominated_by - dom[current].sum(0)
        n_dominated_by[rank >= 0] = -1     # 已分层的个体不再参与
        current = np.where(n_dominated_by == 0)[0]
        r += 1
    return rank


def crowding_distance(F):
    N, M = F.shape
    cd = np.zeros(N)
    if N <= 2:
        return np.full(N, np.inf)
    for k in range(M):
        idx = np.argsort(F[:, k])
        span = F[idx[-1], k] - F[idx[0], k]
        cd[idx[0]] = cd[idx[-1]] = np.inf
        if span > 0:
            cd[idx[1:-1]] += (F[idx[2:], k] - F[idx[:-2], k]) / span
    return cd


def tournament(rank, cd, n, rng):
    a, b = rng.integers(0, len(rank), (2, n))
    better_a = (rank[a] < rank[b]) | ((rank[a] == rank[b]) & (cd[a] > cd[b]))
    return np.where(better_a, a, b)


def variation(parents, K, rng, pc=0.9, pm=None):
    """均匀交叉 + 随机重置变异"""
    n, L = parents.shape
    pm = 1.0 / L if pm is None else pm
    p1, p2 = parents[: n // 2], parents[n // 2: n // 2 * 2]
    mask = (rng.random(p1.shape) < 0.5) & (rng.random((len(p1), 1)) < pc)
    c1, c2 = np.where(mask, p2, p1), np.where(mask, p1, p2)
    kids = np.vstack([c1, c2])
    mut = rng.random(kids.shape) < pm
    kids[mut] = rng.integers(0, K + 1, mut.sum())
    return kids


def nsga2_survival(F, N):
    rank = fast_non_dominated_sort(F)
    chosen = []
    for r in range(rank.max() + 1):
        front = np.where(rank == r)[0]
        if len(chosen) + len(front) <= N:
            chosen.extend(front)
        else:
            cd = crowding_distance(F[front])
            chosen.extend(front[np.argsort(-cd)[: N - len(chosen)]])
            break
    return np.array(chosen)


def run_nsga(problem, algo="nsga2", pop_size=100, n_gen=300, seed=0, ref_dirs=None, log_every=10):
    """通用主循环：algo ∈ {'nsga2', 'nsga3'}；返回最终种群、目标值和每代前沿历史"""
    rng = np.random.default_rng(seed)
    pop = problem.random_population(pop_size, rng)
    F = problem.evaluate(pop)
    history = []
    for gen in range(n_gen):
        if algo == "nsga2":
            rank = fast_non_dominated_sort(F)
            cd = np.zeros(len(F))
            for r in np.unique(rank):
                cd[rank == r] = crowding_distance(F[rank == r])
            parents = pop[tournament(rank, cd, pop_size, rng)]
        else:                                                 # NSGA-III 原文：随机配对
            parents = pop[rng.integers(0, pop_size, pop_size)]
        kids = variation(parents, problem.K, rng)
        pop_all, F_all = np.vstack([pop, kids]), np.vstack([F, problem.evaluate(kids)])
        if algo == "nsga2":
            keep = nsga2_survival(F_all, pop_size)
        else:
            keep = nsga3_survival(F_all, pop_size, ref_dirs, rng)
        pop, F = pop_all[keep], F_all[keep]
        if gen % log_every == 0 or gen == n_gen - 1:
            history.append((gen, F[fast_non_dominated_sort(F) == 0].copy()))
    front = fast_non_dominated_sort(F) == 0
    return pop[front], F[front], history

## Cell 9 (markdown)

## A.3 NSGA-III

NSGA-II 的拥挤距离在 3 个及以上目标时效果变差（高维空间里几乎所有点都"不拥挤"）。
NSGA-III（Deb & Jain, 2014）保留非支配排序，但把**拥挤距离换成参考点（reference points）引导的小生境保留**：

1. 在归一化超平面上均匀生成参考方向（Das-Dennis 方法，$H$ 等分 $M$ 个目标，共 $\binom{H+M-1}{M-1}$ 个）。
2. **自适应归一化**：用理想点 $z^*$ 平移，用极值点构造超平面求截距 $a_k$，得到 $\tilde f_k = (f_k - z^*_k)/a_k$。
3. **关联**：每个个体关联到垂直距离最近的参考方向。
4. **小生境保留**：最后一层放不下时，反复挑"已关联个体最少"的参考方向，从该方向上选一个个体（若该方向还没人，就选垂直距离最近的）。

效果：解沿参考方向**均匀**铺开，不依赖拥挤距离。

## Cell 10 (code)

def das_dennis(n_obj, n_partitions):
    """Das-Dennis 均匀参考方向"""
    def rec(left, depth):
        if depth == n_obj - 1:
            return [[left]]
        return [[i] + rest for i in range(left + 1) for rest in rec(left - i, depth + 1)]
    return np.array(rec(n_partitions, 0), float) / n_partitions


def normalize(F, ideal):
    """NSGA-III 自适应归一化：极值点 -> 超平面截距；失败时退化为 nadir 归一化"""
    Fp = F - ideal
    M = F.shape[1]
    w = np.eye(M) + 1e-6
    asf = (Fp[:, None, :] / w[None, :, :]).max(-1)        # (N, M)
    extreme = Fp[asf.argmin(0)]                            # 每个轴的极值点
    try:
        b = np.linalg.solve(extreme, np.ones(M))
        intercept = 1.0 / b
        if np.any(intercept <= 1e-6) or not np.all(np.isfinite(intercept)):
            raise np.linalg.LinAlgError
    except np.linalg.LinAlgError:
        intercept = Fp.max(0)
    intercept = np.where(intercept <= 1e-6, Fp.max(0) + 1e-6, intercept)
    return Fp / intercept


def associate(Fn, ref_dirs):
    """返回每个个体最近的参考方向编号及垂直距离"""
    u = ref_dirs / np.linalg.norm(ref_dirs, axis=1, keepdims=True)
    proj = np.einsum("nk,rk->nr", Fn, u)                  # (N, R) 投影长度
    perp = np.sqrt(np.maximum((Fn ** 2).sum(1, keepdims=True) - proj ** 2, 0))
    niche = perp.argmin(1)
    return niche, perp[np.arange(len(Fn)), niche]


def nsga3_survival(F, N, ref_dirs, rng):
    rank = fast_non_dominated_sort(F)
    chosen, last = [], None
    for r in range(rank.max() + 1):
        front = np.where(rank == r)[0]
        if len(chosen) + len(front) <= N:
            chosen.extend(front)
            if len(chosen) == N:
                return np.array(chosen)
        else:
            last = front
            break
    if last is None:
        return np.array(chosen)
    cand = np.array(chosen + list(last))
    Fn = normalize(F[cand], F[cand].min(0))
    niche, dist = associate(Fn, ref_dirs)
    k = len(chosen)
    niche_count = np.bincount(niche[:k], minlength=len(ref_dirs))
    pool = list(range(k, len(cand)))                       # 最后一层在 cand 中的下标
    excluded = np.zeros(len(ref_dirs), bool)
    while len(chosen) < N:
        counts = np.where(excluded, np.inf, niche_count)
        j_min = rng.choice(np.where(counts == counts.min())[0])
        members = [p for p in pool if niche[p] == j_min]
        if not members:
            excluded[j_min] = True
            continue
        pick = members[int(np.argmin(dist[members]))] if niche_count[j_min] == 0 else rng.choice(members)
        chosen.append(cand[pick])
        pool.remove(pick)
        niche_count[j_min] += 1
    return np.array(chosen)


print("2 目标 99 等分 -> 参考方向数", len(das_dennis(2, 99)))
print("3 目标 13 等分 -> 参考方向数", len(das_dennis(3, 13)))

## Cell 11 (markdown)

## A.4 评价指标与对照组

- **超体积 HV (Hypervolume)**：前沿与参考点围成的目标空间体积，越大越好，同时反映**收敛性**和**分布性**。所有算法用同一套归一化（理想点 / 最差点）和同一参考点 $(1.1, 1.1)$。
- **对照组：加权和 + KM**。把两个目标线性加权 $w_{ij}=\text{fare}_j-\lambda\, d^{\text{pick}}_{ij}$，扫描 $\lambda$ 并用 KM 求最大权匹配。每个 $\lambda$ 得到一个解。
  注意：加权和只能找到前沿**凸包**上的点（supported solutions），凹陷部分的帕累托解永远找不到，这正是进化多目标算法的优势。

## Cell 12 (code)

def hv2d(F, ref):
    F = F[(F < ref).all(1)]
    if len(F) == 0:
        return 0.0
    F = F[np.argsort(F[:, 0])]
    hv, best_f2 = 0.0, ref[1]
    for f1, f2 in F:
        if f2 < best_f2:
            hv += (ref[0] - f1) * (best_f2 - f2)
            best_f2 = f2
    return hv


def hv3d(F, ref):
    F = F[(F < ref).all(1)]
    if len(F) == 0:
        return 0.0
    F = F[np.argsort(F[:, 2])]
    hv = 0.0
    for i in range(len(F)):
        top = F[i + 1, 2] if i + 1 < len(F) else ref[2]
        hv += hv2d(F[: i + 1, :2], ref[:2]) * (top - F[i, 2])
    return hv


def hypervolume(F, ideal, nadir):
    Fn = (F - ideal) / np.maximum(nadir - ideal, 1e-12)
    ref = np.full(F.shape[1], 1.1)
    return hv2d(Fn, ref) if F.shape[1] == 2 else hv3d(Fn, ref)


def km_weighted_sum(problem, lambdas):
    """加权和 + KM：每个 λ 返回一个目标向量（只在与 NSGA 相同的候选边上匹配）"""
    feas = np.zeros_like(problem.pickup, bool)
    for j in range(problem.n_var):
        c = problem.cand[j][problem.cand[j] >= 0]
        feas[c, j] = True
    out = []
    for lam in lambdas:
        W = np.where(feas, problem.fare[None, :] - lam * problem.pickup, 0.0)
        W = np.maximum(W, 0.0)                         # 负收益的边等价于"不派"
        r, c = linear_sum_assignment(-W)
        keep = W[r, c] > 0
        d, j = r[keep], c[keep]
        f = [-problem.fare[j].sum(), problem.pickup[d, j].sum()]
        if problem.n_obj == 3:
            f.append(-keep.sum())
        out.append(f)
    return np.array(out)


def knee_point(F):
    """离"两端点连线"最远的点：边际收益突变处，常作为折中解推荐给决策者"""
    Fn = (F - F.min(0)) / np.maximum(F.max(0) - F.min(0), 1e-12)
    a, b = Fn[Fn[:, 0].argmin()], Fn[Fn[:, 0].argmax()]
    v, w = b - a, Fn - a
    d = np.abs(v[0] * w[:, 1] - v[1] * w[:, 0]) / (np.linalg.norm(v) + 1e-12)
    return int(d.argmax())


LAMBDAS = np.concatenate([[0.0], np.geomspace(0.05, 60, 40)])

## Cell 13 (markdown)

## A.5 实验 1：晚高峰批次的帕累托前沿（2 目标）

## Cell 14 (code)

REF2 = das_dennis(2, 99)                                  # 100 个参考方向
t0 = time.time()
_, F_n2, hist_n2 = run_nsga(prob, "nsga2", pop_size=100, n_gen=300, seed=SEED)
_, F_n3, hist_n3 = run_nsga(prob, "nsga3", pop_size=100, n_gen=300, seed=SEED, ref_dirs=REF2)
F_km = km_weighted_sum(prob, LAMBDAS)
print(f"耗时 {time.time() - t0:.1f}s | NSGA-II 前沿 {len(F_n2)} 个解, NSGA-III 前沿 {len(F_n3)} 个解")

allF = np.vstack([F_n2, F_n3, F_km])
IDEAL2, NADIR2 = allF.min(0), allF.max(0)
for name, F in [("NSGA-II", F_n2), ("NSGA-III", F_n3), ("加权和+KM", F_km)]:
    print(f"{name:10s} HV = {hypervolume(F, IDEAL2, NADIR2):.4f}")

## Cell 15 (code)

fig, ax = plt.subplots(figsize=(7.5, 5.2))
ax.scatter(F_n2[:, 1], -F_n2[:, 0], s=22, label="NSGA-II", color="#4c78a8")
ax.scatter(F_n3[:, 1], -F_n3[:, 0], s=22, marker="^", label="NSGA-III", color="#f58518", alpha=0.8)
ax.plot(F_km[:, 1], -F_km[:, 0], "k--o", ms=4, lw=1, label="加权和 + KM（扫描 λ）")
k = knee_point(F_n2)
ax.scatter(F_n2[k, 1], -F_n2[k, 0], s=180, facecolors="none", edgecolors="#9F3A3D", lw=2, label="膝点（推荐折中解）")
greedy = prob.evaluate_one(np.ones(prob.n_var, int))
ax.scatter(greedy[1], -greedy[0], s=120, marker="*", color="#54a24b", label="贪心：全派最近司机", zorder=5)
ax.set(xlabel="总接驾距离 / km（越小越好）", ylabel="平台总收入 / 元（越大越好）",
       title=f"帕累托前沿：18 点批次（{prob.n_drivers} 司机 / {prob.n_var} 订单）")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/pareto_2obj.png", dpi=200)
plt.show()

i_max = F_n2[:, 0].argmin()
print(f"贪心（全派最近）：收入 {-greedy[0]:.1f} 元，接驾 {greedy[1]:.1f} km")
print(f"NSGA-II 收入最高解：收入 {-F_n2[i_max, 0]:.1f} 元，接驾 {F_n2[i_max, 1]:.1f} km")
print(f"NSGA-II 膝点：      收入 {-F_n2[k, 0]:.1f} 元，接驾 {F_n2[k, 1]:.1f} km")

## Cell 16 (markdown)

## A.6 实验 2：收敛曲线（5 个随机种子）

每 10 代记录一次当前第一层前沿的 HV，观察两种算法的收敛速度与稳定性。

## Cell 17 (code)

SEEDS = [0, 1, 2, 3, 4]
hv_curves = {"NSGA-II": [], "NSGA-III": []}
final_fronts = {"NSGA-II": [], "NSGA-III": []}
t0 = time.time()
for s in SEEDS:
    for name, algo in [("NSGA-II", "nsga2"), ("NSGA-III", "nsga3")]:
        _, F, hist = run_nsga(prob, algo, pop_size=100, n_gen=300, seed=s, ref_dirs=REF2)
        final_fronts[name].append(F)
        hv_curves[name].append([(g, hypervolume(h, IDEAL2, NADIR2)) for g, h in hist])
print(f"耗时 {time.time() - t0:.1f}s")

fig, ax = plt.subplots(figsize=(7, 4.5))
for name, color in [("NSGA-II", "#4c78a8"), ("NSGA-III", "#f58518")]:
    arr = np.array(hv_curves[name])                  # (seed, point, 2)
    gens, hv = arr[0, :, 0], arr[:, :, 1]
    ax.plot(gens, hv.mean(0), color=color, label=name)
    ax.fill_between(gens, hv.min(0), hv.max(0), color=color, alpha=0.2)
ax.axhline(hypervolume(F_km, IDEAL2, NADIR2), color="k", ls="--", label="加权和 + KM")
ax.set(xlabel="代数", ylabel="超体积 HV", title="收敛曲线（均值 ± 极差，5 个种子）")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/hv_convergence.png", dpi=200)
plt.show()

for name in hv_curves:
    final = np.array(hv_curves[name])[:, -1, 1]
    print(f"{name:9s} 最终 HV = {final.mean():.4f} ± {final.std():.4f}")

## Cell 18 (markdown)

## A.7 实验 3：加入第三个目标 —— NSGA-III 的主场

第三个目标：**最大化服务订单数**（应答率）。收入高的方案偏好长途单，服务单数多的方案偏好短途单，接驾距离又希望少派单 —— 三者两两冲突。
目标数 ≥ 3 时，NSGA-III 的参考点机制通常比 NSGA-II 的拥挤距离分布更均匀。

## Cell 19 (code)

def spacing(F, ideal, nadir):
    """Spacing 指标：归一化后每个解到最近邻的距离的变异系数，越小越均匀"""
    Fn = np.unique((F - ideal) / np.maximum(nadir - ideal, 1e-12), axis=0)
    D = np.abs(Fn[:, None] - Fn[None]).sum(-1)
    np.fill_diagonal(D, np.inf)
    d = D.min(1)
    return d.std() / d.mean()


prob3 = DispatchProblem(batch, n_obj=3)
REF3 = das_dennis(3, 13)                                   # 105 个参考方向
hv3 = {"NSGA-II": [], "NSGA-III": []}
fronts3 = {}
t0 = time.time()
for s in SEEDS:
    for name, algo in [("NSGA-II", "nsga2"), ("NSGA-III", "nsga3")]:
        _, F, _ = run_nsga(prob3, algo, pop_size=105, n_gen=300, seed=s, ref_dirs=REF3, log_every=1000)
        fronts3.setdefault(name, []).append(F)
F_km3 = km_weighted_sum(prob3, LAMBDAS)
all3 = np.vstack([f for v in fronts3.values() for f in v] + [F_km3])
IDEAL3, NADIR3 = all3.min(0), all3.max(0)
for name in fronts3:
    hv3[name] = [hypervolume(F, IDEAL3, NADIR3) for F in fronts3[name]]
    sp = [spacing(F, IDEAL3, NADIR3) for F in fronts3[name]]
    print(f"{name:9s} 3 目标 HV = {np.mean(hv3[name]):.4f} ± {np.std(hv3[name]):.4f} | Spacing = {np.mean(sp):.3f}")
print(f"加权和+KM 3 目标 HV = {hypervolume(F_km3, IDEAL3, NADIR3):.4f}   耗时 {time.time() - t0:.1f}s")

## Cell 20 (code)

fig = plt.figure(figsize=(12, 5))
for i, (name, color) in enumerate([("NSGA-II", "#4c78a8"), ("NSGA-III", "#f58518")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    F = fronts3[name][0]
    ax.scatter(F[:, 1], -F[:, 0], -F[:, 2], c=color, s=14)
    ax.set(xlabel="接驾距离 / km", ylabel="收入 / 元", zlabel="服务单数",
           title=f"{name}（HV={hv3[name][0]:.3f}，{len(F)} 个解）")
    ax.view_init(elev=22, azim=-60)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/pareto_3obj.png", dpi=200)
plt.show()

## Cell 21 (markdown)

**为什么 NSGA-III 在派单问题上没占到便宜？** 派单的 3 目标前沿近似**退化**：服务单数与收入高度相关，前沿是一条"细带"而不是一张铺满的曲面，
大量参考方向上根本没有解，参考点机制的优势发挥不出来。

下面用经典测试函数 **DTLZ2**（3 目标，真实前沿是单位球面的 1/8）做对照：前沿铺满整个曲面时，NSGA-III 在**收敛性**（到球面的距离）、**均匀性**（Spacing）和 HV 上都优于 NSGA-II。
结论：**算法选择取决于前沿形状与目标数**，不是"新算法一定更好"。

## Cell 22 (code)

class DTLZ2:
    """DTLZ2 测试函数（变量离散为 0..K 的整数，复用上面的整数编码 GA 算子）"""

    def __init__(self, n_obj=3, n_var=12, K=200):
        self.n_obj, self.n_var, self.K = n_obj, n_var, K

    def random_population(self, size, rng):
        return rng.integers(0, self.K + 1, (size, self.n_var))

    def evaluate(self, pop):
        x, M = pop / self.K, self.n_obj
        g = ((x[:, M - 1:] - 0.5) ** 2).sum(1)
        F = np.ones((len(x), M)) * (1 + g)[:, None]
        for i in range(M):
            F[:, i] *= np.prod(np.cos(x[:, : M - 1 - i] * np.pi / 2), 1)
            if i > 0:
                F[:, i] *= np.sin(x[:, M - 1 - i] * np.pi / 2)
        return F


dtlz = DTLZ2()
fig = plt.figure(figsize=(12, 5))
for i, (name, algo, color) in enumerate([("NSGA-II", "nsga2", "#4c78a8"), ("NSGA-III", "nsga3", "#f58518")]):
    _, F, _ = run_nsga(dtlz, algo, pop_size=92, n_gen=400, seed=1, ref_dirs=das_dennis(3, 12), log_every=1000)
    err = np.abs(np.linalg.norm(F, axis=1) - 1).mean()
    sp, hv = spacing(F, np.zeros(3), np.ones(3)), hypervolume(F, np.zeros(3), np.ones(3))
    print(f"{name:9s} DTLZ2: 到真实前沿距离 {err:.4f} | Spacing {sp:.3f} | HV {hv:.4f}")
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    ax.scatter(F[:, 0], F[:, 1], F[:, 2], c=color, s=14)
    ax.set(title=f"{name} on DTLZ2（Spacing={sp:.2f}，越小越均匀）", xlabel="f1", ylabel="f2", zlabel="f3")
    ax.view_init(elev=25, azim=45)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/dtlz2_compare.png", dpi=200)
plt.show()

## Cell 23 (markdown)

## A.8 实验 4：不同时段的帕累托前沿

同样 40 个司机，在早高峰（8 点）、午间（13 点）、晚高峰（18 点）、深夜（23 点）各抽一个批次，比较前沿形状。

## Cell 24 (code)

fig, ax = plt.subplots(figsize=(7.5, 5))
for hour, color in [(8, "#4c78a8"), (13, "#54a24b"), (18, "#9F3A3D"), (23, "#b279a2")]:
    p = DispatchProblem(make_batch(trips_train, hour=hour, seed=SEED))
    _, F, _ = run_nsga(p, "nsga2", pop_size=100, n_gen=300, seed=SEED, log_every=1000)
    F = F[np.argsort(F[:, 1])]
    ax.plot(F[:, 1], -F[:, 0], "o-", ms=3, color=color, label=f"{hour}:00（可行订单 {(p.n_cand > 0).sum()}）")
ax.set(xlabel="总接驾距离 / km", ylabel="平台总收入 / 元", title="不同时段批次的帕累托前沿（NSGA-II）")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/pareto_by_hour.png", dpi=200)
plt.show()

## Cell 25 (markdown)

### Part A 思考题

1. 加权和 + KM 在本实验中表现不差，为什么？（提示：观察前沿形状是否"凸"。）什么情况下加权和会漏掉帕累托解？
2. 2 目标时 NSGA-II 与 NSGA-III 谁更好？3 目标时呢？结合"拥挤距离"与"参考点"的原理解释。
3. 前沿的高收入端，NSGA 的解比 KM 稍差。请尝试：(a) 增大代数/种群；(b) 用 KM 的解初始化部分个体（混合策略），观察 HV 变化。
4. 平台运营中要从前沿上选**一个**方案，你会怎么选？膝点、约束法（接驾距离 ≤ X km 下收入最大）各有什么优缺点？

## Cell 26 (markdown)

# Part B 强化学习派单：Q-learning + KM（Q-KM）

## B.1 为什么要看"长期价值"

KM 最大化**当前批次**的收入，是**短视（myopic）**的：一个 30 元的订单把司机送到郊区，送完后他可能 1 小时接不到单；一个 25 元的订单把司机送到市中心，马上又能接下一单。
平台真正关心的是**全天总收入**，这是一个**序贯决策**问题 —— 用 MDP / 强化学习建模。

## B.2 平台视角的 MDP（参考 KDD'18 滴滴 *Large-Scale Order Dispatch*）

如果把每辆车的精确位置都当作状态，状态空间爆炸；KDD'18 的做法是**把整个平台当作一个智能体**，学习"区域级"的价值表，再把它嵌入 KM：

| MDP 要素 | 本实验中的定义 |
|---|---|
| 状态 $s=(t, i)$ | 时间片 $t$（10 分钟一片，6:00~24:00 共 108 片）× 司机所在区域 $i$（8×8=64 个网格） |
| 动作 $a$ | 派往区域 $j$ 的订单（送客到 $j$），或"空等"（WAIT） |
| 奖励 $r$ | 订单车费（空等为 0） |
| 转移 | 接单：$(t,i)\to(t+\Delta, j)$，$\Delta$ = 接驾 + 送客时间片数；空等：$(t,i)\to(t+1,i)$ |
| 折扣 | $\gamma^{\Delta}$（半马尔可夫，动作持续多少时间片就折扣多少次） |

所有司机**共享**同一张 Q 表 $Q(t, i, a)$：每个司机的每一次接单/空等都是一条经验，规模只有 $108\times64\times65$，与车辆数无关。

## Cell 27 (code)

GRID = 8
N_ZONES = GRID * GRID
WAIT = N_ZONES                       # 动作编号 64 = 空等
STEP_MIN = 10                        # 时间片长度（分钟）
DAY_START, DAY_END = 6 * 60, 24 * 60
T = (DAY_END - DAY_START) // STEP_MIN  # 108 个时间片
SPEED_KMH = 25.0
KM_PER_STEP = SPEED_KMH * STEP_MIN / 60  # 每个时间片行驶约 4.2 km
PATIENCE = 2                         # 订单最多等 2 个时间片（20 分钟）未派则取消
ORDERS_PER_DAY = 1500


def zone_of(x, y):
    col = np.clip((x / W_KM * GRID).astype(int), 0, GRID - 1)
    row = np.clip((y / H_KM * GRID).astype(int), 0, GRID - 1)
    return row * GRID + col


ZONE_XY = np.array([((c + 0.5) * W_KM / GRID, (r + 0.5) * H_KM / GRID)
                    for r in range(GRID) for c in range(GRID)])
# 区域中心之间的行驶时间片数 Δ(i, j)，用于区域级价值估计（至少 1 片）
DELTA = np.maximum(1, np.ceil(np.abs(ZONE_XY[:, None] - ZONE_XY[None]).sum(-1) / KM_PER_STEP)).astype(int)


def sample_episode(trip_pool, n_drivers, seed):
    """一天的订单 = 从历史订单池按时间分布有放回抽样 + 小幅时空扰动；司机初始位置来自早上签到热点"""
    rng = np.random.default_rng(seed)
    pool = trip_pool[(trip_pool.minute >= DAY_START) & (trip_pool.minute < DAY_END)]
    od = pool.iloc[rng.integers(0, len(pool), ORDERS_PER_DAY)]
    minute = np.clip(od.minute.values + rng.integers(-5, 6, ORDERS_PER_DAY), DAY_START, DAY_END - 1)
    jit = lambda v, hi: np.clip(v + rng.normal(0, 0.3, len(v)), 0, hi)
    ox, oy = jit(od.ox.values, W_KM), jit(od.oy.values, H_KM)
    dx, dy = jit(od.dx.values, W_KM), jit(od.dy.values, H_KM)
    order = np.argsort(minute, kind="stable")
    trip_km = np.abs(ox - dx) + np.abs(oy - dy)
    orders = dict(step=((minute - DAY_START) // STEP_MIN)[order],
                  oxy=np.c_[ox, oy][order], dzone=zone_of(dx, dy)[order], dxy=np.c_[dx, dy][order],
                  trip_km=trip_km[order], fare=(BASE_FARE + PER_KM * trip_km)[order])
    morning = ck[(ck.minute >= 360) & (ck.minute < 480)][["x", "y"]].values
    drv = morning[rng.integers(0, len(morning), n_drivers)] + rng.normal(0, 0.5, (n_drivers, 2))
    drv = np.clip(drv, 0, [W_KM, H_KM])
    return orders, drv


def run_episode(episode, policy, collect=False):
    """
    按时间片推进一天。policy(ctx) 返回 [(司机局部下标, 订单局部下标), ...]
    collect=True 时返回经验 (t, 区域 i, 动作 a, 奖励 r, 下一时间片 t', 下一区域 i', avail)
    其中 avail 是该司机在 t' 时刻（下一次空闲时）接驾半径内订单的目的地区域集合 A(s')
    """
    orders, drv0 = episode
    pos = drv0.copy()
    zone = zone_of(pos[:, 0], pos[:, 1])
    free_at = np.zeros(len(pos), int)
    active = np.zeros(0, int)
    ptr, n_orders = 0, len(orders["step"])
    revenue = pickup_km = 0.0
    served = 0
    trans = []
    pending = {}                                  # 司机 -> 尚未填写 avail 的上一条经验
    no_avail = np.zeros(0, int)
    for t in range(T):
        new_end = ptr
        while new_end < n_orders and orders["step"][new_end] == t:
            new_end += 1
        active = np.concatenate([active, np.arange(ptr, new_end)])
        ptr = new_end
        active = active[t - orders["step"][active] <= PATIENCE]          # 超时取消
        idle = np.where(free_at <= t)[0]
        pairs = []
        if len(idle) and len(active):
            P = np.abs(pos[idle][:, None] - orders["oxy"][active][None]).sum(-1)
            ctx = dict(t=t, pickup=P, feas=P <= PICKUP_RADIUS, fare=orders["fare"][active],
                       drv_zone=zone[idle], dest_zone=orders["dzone"][active])
            pairs = policy(ctx)
        if collect:                               # 回填上一条经验的 A(s')
            for a, d in enumerate(idle):
                if d in pending:
                    pending.pop(d)[6] = (np.unique(ctx["dest_zone"][ctx["feas"][a]])
                                         if len(active) else no_avail)
        busy = set()
        done = []
        for a, b in pairs:
            d, o = idle[a], active[b]
            pk = abs(pos[d, 0] - orders["oxy"][o, 0]) + abs(pos[d, 1] - orders["oxy"][o, 1])
            assert pk <= PICKUP_RADIUS + 1e-9, "派单违反了接驾半径约束"
            dur = max(1, int(math.ceil((pk + orders["trip_km"][o]) / KM_PER_STEP)))
            fare = orders["fare"][o]
            if collect:
                trans.append([t, zone[d], orders["dzone"][o], fare, t + dur, orders["dzone"][o], no_avail])
                pending[d] = trans[-1]
            revenue += fare
            pickup_km += pk
            served += 1
            pos[d] = orders["dxy"][o]
            zone[d] = orders["dzone"][o]
            free_at[d] = t + dur
            busy.add(d)
            done.append(b)
        if collect:
            for d in idle:
                if d not in busy:
                    trans.append([t, zone[d], WAIT, 0.0, t + 1, zone[d], no_avail])
                    pending[d] = trans[-1]
        active = np.delete(active, done)
    metrics = dict(revenue=revenue, answer_rate=served / n_orders,
                   avg_pickup=pickup_km / max(served, 1), served=served)
    return metrics, trans

## Cell 28 (markdown)

## B.3 三个基线策略（已给出）

- **贪心最近**：订单按到达顺序，每单派给最近的空闲司机（实验二的思路）。
- **KM-即时收入**：每个时间片做一次 KM，边权 = 车费，最大化当前批次总收入（短视）。
- **随机 KM**：边权随机，仅用于训练时**探索**。

## Cell 29 (code)

def km_max(W):
    """最大权匹配：W<=0 的边视为不连（等价于不派），返回 [(行, 列), ...]"""
    W = np.where(W > 0, W, 0.0)
    r, c = linear_sum_assignment(-W)
    keep = W[r, c] > 0
    return list(zip(r[keep], c[keep]))


def greedy_nearest(ctx):
    used, pairs = set(), []
    for b in range(ctx["pickup"].shape[1]):
        cand = [a for a in np.argsort(ctx["pickup"][:, b]) if ctx["feas"][a, b] and a not in used]
        if cand:
            used.add(cand[0])
            pairs.append((cand[0], b))
    return pairs


def km_fare(ctx):
    return km_max(np.where(ctx["feas"], ctx["fare"][None, :], 0.0))


_explore_rng = np.random.default_rng(SEED)


def random_km(ctx):
    return km_max(np.where(ctx["feas"], _explore_rng.random(ctx["feas"].shape) + 0.01, 0.0))


ep_demo = sample_episode(trips_train, n_drivers=60, seed=SEED)
for name, pol in [("贪心最近", greedy_nearest), ("KM-即时收入", km_fare)]:
    m, _ = run_episode(ep_demo, pol)
    print(f"{name:8s} 收入 {m['revenue']:8.0f} 元 | 应答率 {m['answer_rate']:.3f} | 平均接驾 {m['avg_pickup']:.2f} km")

## Cell 30 (markdown)

## B.4 Q-learning：学习区域到区域的长期价值

Q-learning 是**无模型、离策略（off-policy）**的时序差分算法。对一条经验 $(s, a, r, s')$：

$$\underbrace{y}_{\text{TD 目标}} = r + \gamma^{\Delta}\max_{a'\in \mathcal{A}(s')} Q(s', a'),\qquad Q(s,a) \leftarrow Q(s,a) + \alpha\,\big(y - Q(s,a)\big)$$

本实验中 $s=(t,i)$，$s'=(t',j)$，$\Delta=t'-t$；若 $t'\ge T$（一天结束），$y=r$。

**派单场景的关键细节：$\max$ 只能在 $s'$ 处"真实可选"的动作 $\mathcal{A}(s')$ 上取。**
司机不能想去哪就去哪，只能接身边出现的订单。$\mathcal{A}(s')$ = 司机到达 $s'$ 时接驾半径内订单的目的地区域 ∪ {空等}。
仿真器已经把每条经验对应的 $\mathcal{A}(s')$ 记录在 `avail` 里。如果在全部 65 个动作上取 max，相当于假设"司机总能接到该区域历史上最好的那一单"，价值会被严重高估。

同时维护**状态价值** $V(t,i)=\mathbb{E}\big[\max_{a\in\mathcal{A}(s)}Q(s,a)\big]$：每算出一次 $\max$，就是 $V(s')$ 的一个样本，用样本平均更新 $V$。

**学习率**：$\alpha = \max(1/N(s,a),\ \alpha_{\min})$，前期等价于样本平均，后期保留跟踪能力。

## Cell 31 (code)

GAMMA = 0.92        # 每个时间片（10 分钟）的折扣因子
ALPHA_MIN = 0.05


class QTable:
    """平台共享的 Q 表（与车辆数无关）"""

    def __init__(self):
        self.Q = np.zeros((T, N_ZONES, N_ZONES + 1))    # Q[t, i, a]，a = 目的地区域 0..63 或 WAIT=64
        self.N = np.zeros((T, N_ZONES, N_ZONES + 1), int)
        self.V = np.zeros((T + 1, N_ZONES))             # V[t, i]；V[T] ≡ 0（一天结束）
        self.NV = np.zeros((T + 1, N_ZONES), int)


def q_update(qt, t, z, a, r, t2, z2, avail, gamma=GAMMA):
    """
    TODO 1：对一条经验做一次 Q-learning 更新（原地修改 qt）。
        经验含义：时间片 t、区域 z 的司机执行动作 a（a = 目的地区域 或 WAIT），获得奖励 r，
                  在时间片 t2 到达区域 z2；avail 是 s'=(t2, z2) 处可选的目的地区域数组（可能为空）。
      1) 若 t2 >= T：m = 0（终止状态）
         否则：  m = max(qt.Q[t2, z2, 可选动作])，可选动作 = avail ∪ {WAIT}（提示：np.append(avail, WAIT)）
                 并用样本 m 更新 V：qt.NV[t2, z2] += 1；qt.V[t2, z2] += (m - qt.V[t2, z2]) / qt.NV[t2, z2]
      2) TD 目标 y = r + gamma ** (t2 - t) * m
      3) qt.N[t, z, a] += 1，学习率 alpha = max(1 / qt.N[t, z, a], ALPHA_MIN)
      4) qt.Q[t, z, a] += alpha * (y - qt.Q[t, z, a])
    返回 TD 误差 (y - 更新前的 Q[t, z, a])，用于监控收敛。
    """
    # 请在此处完成代码
    raise NotImplementedError("请完成 TODO")


# 单元测试：手算验证
_qt = QTable()
_qt.Q[5, 3, 7], _qt.Q[5, 3, 9], _qt.Q[5, 3, WAIT] = 30.0, 99.0, 10.0
td = q_update(_qt, 2, 0, 3, 20.0, 5, 3, np.array([7]))
assert abs(td - (20 + GAMMA ** 3 * 30)) < 1e-9, "max 只能在 avail ∪ {WAIT} 上取：应为 30，而不是 99"
assert _qt.N[2, 0, 3] == 1 and abs(_qt.Q[2, 0, 3] - (20 + GAMMA ** 3 * 30)) < 1e-9, "首次访问 alpha=1"
assert abs(_qt.V[5, 3] - 30) < 1e-9, "V(s') 应更新为样本 m 的平均"
q_update(_qt, 2, 0, 3, 0.0, 5, 3, np.array([], int))      # 无订单可接：m = Q[WAIT] = 10
assert abs(_qt.Q[2, 0, 3] - (20 + GAMMA ** 3 * 30 + GAMMA ** 3 * 10) / 2) < 1e-9, "第二次 alpha=1/2"
assert abs(_qt.V[5, 3] - 20) < 1e-9
assert abs(q_update(_qt, T - 1, 0, WAIT, 7.0, T + 2, 1, np.array([5])) - 7.0) < 1e-9, "终止状态只有 r"
print("TODO 1 通过测试 ✓")

## Cell 32 (markdown)

## B.5 Q-KM：把长期价值嵌入 KM 的边权

对每个时间片的二部图（空闲司机 × 待派订单），KDD'18 把边权从"即时收入"改成"即时收入 + 长期价值增量"：

$$w_{dj} = \underbrace{\text{fare}_j}_{\text{即时奖励}} + \beta\cdot LT(t,i,k),\qquad
LT(t,i,k)=\underbrace{\gamma^{\Delta(i,k)}\,V\big(t+\Delta(i,k),\,k\big)}_{\text{送完客后在目的地 }k\text{ 的价值}}-\underbrace{\gamma\,V(t+1,\,i)}_{\text{不派、原地等一个时间片的价值}}$$

其中 $i$ 是司机所在区域，$k$ 是订单目的地区域。直观解释：
- 第一项：送完这单后，司机在目的地还能赚多少（折现到现在）；
- 第二项：**机会成本** —— 这个司机如果这一轮不派单，留在 $i$ 等下一轮的价值（即 $Q(t,i,\text{WAIT})$）；
- $w_{dj}\le 0$ 说明"派这一单还不如让司机等着"（例如把热门区域的司机拉去冷门区域），KM 会选择不派。

**关键：不对每辆车单独计算**。$LT$ 只依赖 (时间片, 起点区域, 终点区域)，每个时间片只需查一张 $64\times64$ 的表，
复杂度与车辆数无关 —— 这正是平台级 RL 能在大规模订单上落地的原因。区域中心间行驶时间片数 `DELTA[i, k]` 已在前面算好。

## Cell 33 (code)

def region_long_term_value(V, gamma=GAMMA):
    """
    TODO 2：由状态价值 V（形状 (T+1, N_ZONES)，V[T]=0）计算区域到区域的长期价值表 LT，形状 (T, N_ZONES, N_ZONES)：
        LT[t, i, k] = gamma^DELTA[i, k] * V[min(t + DELTA[i, k], T), k]  -  gamma * V[t + 1, i]
    提示：可以用 for t in range(T) 循环，每个 t 内用 numpy 向量化：
        t2 = np.minimum(t + DELTA, T)                  # (Z, Z)
        V[t2, np.arange(N_ZONES)[None, :]]             # 取出 V[t2[i,k], k]，形状 (Z, Z)
        V[t + 1][:, None]                              # 每行（起点 i）的等待价值，广播到 (Z, Z)
    """
    # 请在此处完成代码
    raise NotImplementedError("请完成 TODO")


def make_q_km(LT, beta=0.5):
    """返回一个派单策略函数（闭包），供 run_episode 调用"""

    def q_km(ctx):
        """
        TODO 3：Q-KM 派单。ctx 中可用的字段：
            ctx["t"]          当前时间片
            ctx["fare"]       (m,)   每个订单的车费（即时奖励）
            ctx["drv_zone"]   (n,)   每个空闲司机所在区域
            ctx["dest_zone"]  (m,)   每个订单目的地区域
            ctx["feas"]       (n, m) 是否满足接驾半径
        步骤：
          1) 查表得到长期价值矩阵 L (n, m)：L[d, j] = LT[t, drv_zone[d], dest_zone[j]]
             （提示：花式索引 LT[t][drv_zone[:, None], dest_zone[None, :]]）
          2) 边权 W = fare[None, :] + beta * L；不可行的边置 0（等价于不连边）
          3) 调用 km_max(W) 求最大权匹配并返回
        """
        # 请在此处完成代码
        raise NotImplementedError("请完成 TODO")

    return q_km


# 单元测试
_V = np.zeros((T + 1, N_ZONES))
_V[:T, 0], _V[:T, 1] = 5.0, 50.0                          # V[T] 保持 0（一天结束）
_LT = region_long_term_value(_V)
assert _LT.shape == (T, N_ZONES, N_ZONES)
assert abs(_LT[10, 0, 1] - (GAMMA ** DELTA[0, 1] * 50 - GAMMA * 5)) < 1e-9
assert abs(_LT[T - 1, 1, 0] - (GAMMA ** DELTA[1, 0] * 0 - GAMMA * 0)) < 1e-9, "越过一天结束时应取 V[T] = 0"
assert abs(_LT[10, 1, 2] - (0 - GAMMA * 50)) < 1e-9
_ctx = dict(t=10, fare=np.array([10.0, 10.0]), drv_zone=np.array([0, 1]),
            dest_zone=np.array([1, 2]), feas=np.array([[True, True], [True, True]]))
_pairs = sorted((int(a), int(b)) for a, b in make_q_km(_LT)(_ctx))
# 司机 1 在高价值区域 1：接去区域 2 的单 w=10-γ·50<0 不派；区域 0 的司机接去区域 1 的单收益最大
assert _pairs == [(0, 0)], f"期望只派 (司机0, 订单0)，实际 {_pairs}"
print("TODO 2 / TODO 3 通过测试 ✓")

## Cell 34 (markdown)

## B.6 训练：ε-贪心采样 + 逆序 Q-learning 更新（已给出，依赖 TODO 1~3）

每个训练回合（一天）：
1. 用当前 Q 表算 $V$ 和 $LT$；以概率 ε 用"随机 KM"探索，否则用 Q-KM 派单，记录所有司机的经验；
2. 回合结束后按时间**逆序**回放经验做 Q-learning 更新（价值从一天的结尾向开头传播，收敛更快）；
3. 每隔若干回合，在固定的验证日上用**纯 Q-KM（ε=0）**评估一次，画学习曲线。

训练用历史订单（前 70% 日期），评估用未来订单（后 30% 日期），检验泛化。

## Cell 35 (code)

BETA = 0.5


def train_q_km(n_drivers, n_episodes=300, beta=None, eps_start=0.5, eps_end=0.05,
               eval_every=20, seed=SEED, verbose=True):
    beta = BETA if beta is None else beta
    qt = QTable()
    rng = np.random.default_rng(seed)
    val_eps = [sample_episode(trips_train, n_drivers, seed=10_000 + k) for k in range(3)]
    curve, td_log = [], []
    t0 = time.time()
    for ep in range(n_episodes):
        eps = eps_start + (eps_end - eps_start) * ep / max(1, n_episodes - 1)
        LT = region_long_term_value(qt.V)
        q_pol = make_q_km(LT, beta)
        policy = lambda ctx: random_km(ctx) if rng.random() < eps else q_pol(ctx)
        _, trans = run_episode(sample_episode(trips_train, n_drivers, seed=seed + ep), policy, collect=True)
        td_abs = [abs(q_update(qt, *tr)) for tr in sorted(trans, key=lambda x: -x[0])]
        td_log.append(np.mean(td_abs))
        if ep % eval_every == 0 or ep == n_episodes - 1:
            pol = make_q_km(region_long_term_value(qt.V), beta)
            rev = np.mean([run_episode(e, pol)[0]["revenue"] for e in val_eps])
            curve.append((ep, rev))
            if verbose:
                print(f"  ep {ep:4d} | ε={eps:.2f} | |TD|={td_log[-1]:6.2f} | 验证收入 {rev:8.0f} | {time.time() - t0:5.1f}s")
    return qt, np.array(curve), np.array(td_log), val_eps


BETA = 0.5          # 长期价值权重（见 B.9 敏感性实验）
N_DRIVERS = 60
qt, curve, td_log, val_eps = train_q_km(N_DRIVERS)

base_val = {name: np.mean([run_episode(e, pol)[0]["revenue"] for e in val_eps])
            for name, pol in [("贪心最近", greedy_nearest), ("KM-即时收入", km_fare)]}

fig, axes = plt.subplots(1, 2, figsize=(13, 4.3))
axes[0].plot(curve[:, 0], curve[:, 1], "o-", color="#9F3A3D", label="Q-KM（ε=0 评估）")
for (name, v), c in zip(base_val.items(), ["#4c78a8", "#f58518"]):
    axes[0].axhline(v, ls="--", color=c, label=name)
axes[0].set(xlabel="训练回合（天）", ylabel="验证日平均总收入 / 元", title=f"学习曲线（{N_DRIVERS} 辆车）")
axes[0].legend()
axes[0].grid(alpha=0.3)
axes[1].plot(td_log, color="#54a24b")
axes[1].set(xlabel="训练回合（天）", ylabel="平均 |TD 误差|", title="TD 误差")
axes[1].grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/rl_learning_curve.png", dpi=200)
plt.show()

## Cell 36 (markdown)

## B.7 学到的区域价值 V(t, i)：潮汐现象

早高峰（8:00）人们从住宅区去曼哈顿，晚高峰（18:00）反过来。V 的热力图反映了"在这个时刻、这个区域有一辆空车值多少钱"。

## Cell 37 (code)

V = qt.V
fig, axes = plt.subplots(1, 4, figsize=(17, 4.4))
for ax, hh in zip(axes, [8, 13, 18, 22]):
    t = (hh * 60 - DAY_START) // STEP_MIN
    im = ax.imshow(V[t].reshape(GRID, GRID), origin="lower", cmap="RdYlGn",
                   extent=[0, W_KM, 0, H_KM], vmin=0, vmax=np.percentile(V[:T], 99))
    ax.scatter(trips.ox.sample(3000, random_state=0), trips.oy.sample(3000, random_state=0), s=0.3, c="k", alpha=0.25)
    ax.set(title=f"V(t, i) @ {hh}:00", xlabel="x / km")
axes[0].set_ylabel("y / km")
fig.colorbar(im, ax=axes, fraction=0.015, pad=0.01, label="状态价值 / 元")
plt.savefig(f"{FIG_DIR}/value_map.png", dpi=200, bbox_inches="tight")
plt.show()

## Cell 38 (markdown)

## B.8 实验：不同车队规模下的对比（测试集 = 未来日期的订单）

每个车队规模单独训练一张 Q 表（与 KDD'18 一致），在 5 个测试日上评估三种策略的总收入、应答率、平均接驾距离。

## Cell 39 (code)

FLEETS = [40, 60, 100]
results = []
q_tables = {}
for nd in FLEETS:
    qt_n, _, _, _ = train_q_km(nd, n_episodes=300, beta=BETA, verbose=False)
    q_tables[nd] = qt_n
    pol_q = make_q_km(region_long_term_value(qt_n.V), BETA)
    test_eps = [sample_episode(trips_test, nd, seed=50_000 + k) for k in range(5)]
    for name, pol in [("贪心最近", greedy_nearest), ("KM-即时收入", km_fare), ("Q-KM", pol_q)]:
        for k, e in enumerate(test_eps):
            m, _ = run_episode(e, pol)
            results.append(dict(fleet=nd, policy=name, day=k, **m))
res = pd.DataFrame(results)
summary = res.groupby(["fleet", "policy"])[["revenue", "answer_rate", "avg_pickup"]].mean().round(3)
print(summary)

## Cell 40 (code)

POLICIES = ["贪心最近", "KM-即时收入", "Q-KM"]
COLORS = ["#4c78a8", "#f58518", "#9F3A3D"]
fig, axes = plt.subplots(1, 3, figsize=(16, 4.3))
x = np.arange(len(FLEETS))
for ax, (col, title) in zip(axes, [("revenue", "全天总收入 / 元"), ("answer_rate", "应答率"), ("avg_pickup", "平均接驾距离 / km")]):
    for i, (p, c) in enumerate(zip(POLICIES, COLORS)):
        g = res[res.policy == p].groupby("fleet")[col]
        ax.bar(x + (i - 1) * 0.26, g.mean().values, 0.26, yerr=g.std().values, capsize=3, color=c, label=p)
    ax.set(xticks=x, xticklabels=[f"{n} 辆" for n in FLEETS], title=title)
    ax.grid(axis="y", alpha=0.3)
    if col == "revenue":
        lo = res[col].min() * 0.85
        ax.set_ylim(lo, None)
axes[0].legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/rl_compare.png", dpi=200)
plt.show()

gain = summary["revenue"].unstack()
print("Q-KM 相对 KM-即时收入的收入提升：", ((gain["Q-KM"] / gain["KM-即时收入"] - 1) * 100).round(2).to_dict(), "%")
print("Q-KM 相对 贪心最近 的收入提升：  ", ((gain["Q-KM"] / gain["贪心最近"] - 1) * 100).round(2).to_dict(), "%")

## Cell 41 (markdown)

## B.9 实验：长期价值权重 β 的敏感性

$\beta=0$ 退化为 KM-即时收入；$\beta$ 太大时 KM 过分相信价值表，拒单太多。

## Cell 42 (code)

betas = [0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
LT60 = region_long_term_value(q_tables[60].V)
test60 = [sample_episode(trips_test, 60, seed=50_000 + k) for k in range(5)]
sens = []
for b in betas:
    ms = [run_episode(e, make_q_km(LT60, b))[0] for e in test60]
    sens.append((b, np.mean([m["revenue"] for m in ms]), np.mean([m["answer_rate"] for m in ms])))
sens = np.array(sens)
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(sens[:, 0], sens[:, 1], "o-", color="#9F3A3D", label="总收入")
ax.set(xlabel="β（长期价值权重）", ylabel="全天总收入 / 元", title="β 敏感性（60 辆车，测试集）")
ax2 = ax.twinx()
ax2.plot(sens[:, 0], sens[:, 2], "s--", color="#4c78a8", label="应答率")
ax2.set_ylabel("应答率")
ax.grid(alpha=0.3)
fig.legend(loc="lower left", bbox_to_anchor=(0.12, 0.15))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/rl_beta.png", dpi=200)
plt.show()

## Cell 43 (markdown)

### Part B 思考题

1. 本仿真中"KM-即时收入"反而不如"贪心最近"，为什么？（提示：长途单把司机带到哪里？司机送完后多久才能接下一单？）
2. Q-KM 的 $LT$ 只按区域计算，同一区域内的所有司机共享同一个价值。这种近似损失了什么？换来了什么？
3. $\beta=1$ 时效果变差。从"每个司机独立取 max，忽略了其他司机抢单"的角度解释 Q-learning 的过估计；你能想到什么改进？（例如 SARSA / 策略评估、Double Q-learning）
4. 尝试修改 `GAMMA`（0.8 / 0.95）、网格大小 `GRID`、`PATIENCE`，观察对结果的影响。
5. （加分）让空闲司机按 $V$ 主动调度到相邻高价值区域（repositioning），能否进一步提升收入？
