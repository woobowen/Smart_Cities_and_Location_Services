## Cell 0 (markdown)

下面是仿真环境，可直接调用，另外附了一份真实订单数据，若同学们结合真实数据优化仿真器，会加分

## Cell 1 (code)

import heapq
import random
import math
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import numpy as np

# ----------------------------
# 数据结构定义
# ----------------------------

@dataclass
class Worker:
    id: int
    loc: Tuple[float, float]  # (x, y)
    arrival_time: float

@dataclass
class Request:
    id: int
    loc: Tuple[float, float]
    arrival_time: float

@dataclass
class Assignment:
    worker_id: int
    request_id: int
    assign_time: float
    delay: float  # = (assign_time - req.arrival_time) + travel_time

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# ----------------------------
# 仿真环境主类
# ----------------------------

class SimulationEnvironment:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        self.workers = []      # List[Worker]
        self.requests = []     # List[Request]
        self.events = []       # Min-heap of (time, type, obj)
        self.assignments = []  # List[Assignment]
        self.next_worker_id = 0
        self.next_request_id = 0

    def generate_synthetic_data(
        self,
        num_workers: int,
        num_requests: int,
        time_range: Tuple[float, float] = (0, 2000),
        space_range: Tuple[float, float] = (0, 1000),
        worker_time_dist: str = "uniform",
        request_time_dist: str = "uniform",
        loc_dist: str = "uniform"
    ):
        """
        Generate synthetic workers and requests.
        """
        t_min, t_max = time_range
        s_min, s_max = space_range

        def sample_time(n, dist):
            if dist == "uniform":
                return np.random.uniform(t_min, t_max, n)
            elif dist == "normal":
                mu, sigma = (t_min + t_max) / 2, (t_max - t_min) / 6
                return np.clip(np.random.normal(mu, sigma, n), t_min, t_max)
            elif dist == "zipf":
                a = 2.0
                # Zipf gives integers; scale to [t_min, t_max]
                vals = np.random.zipf(a, n)
                vals = (vals - vals.min()) / (vals.max() - vals.min() + 1e-8)
                return t_min + vals * (t_max - t_min)
            else:
                raise ValueError(f"Unknown time distribution: {dist}")

        def sample_loc(n):
            if loc_dist == "uniform":
                return [(random.uniform(s_min, s_max), random.uniform(s_min, s_max)) for _ in range(n)]
            elif loc_dist == "normal":
                mu, sigma = (s_min + s_max) / 2, (s_max - s_min) / 6
                xs = np.clip(np.random.normal(mu, sigma, n), s_min, s_max)
                ys = np.clip(np.random.normal(mu, sigma, n), s_min, s_max)
                return list(zip(xs, ys))
            else:
                raise ValueError(f"Unknown location distribution: {loc_dist}")

        # Generate workers
        worker_times = sample_time(num_workers, worker_time_dist)
        worker_locs = sample_loc(num_workers)
        for t, loc in zip(worker_times, worker_locs):
            w = Worker(id=self.next_worker_id, loc=loc, arrival_time=t)
            self.workers.append(w)
            heapq.heappush(self.events, (t, 'worker', w))
            self.next_worker_id += 1

        # Generate requests
        request_times = sample_time(num_requests, request_time_dist)
        request_locs = sample_loc(num_requests)
        for t, loc in zip(request_times, request_locs):
            r = Request(id=self.next_request_id, loc=loc, arrival_time=t)
            self.requests.append(r)
            heapq.heappush(self.events, (t, 'request', r))
            self.next_request_id += 1

    def reset(self):
        self.events.clear()
        self.assignments.clear()
        self.workers.clear()
        self.requests.clear()
        self.next_worker_id = 0
        self.next_request_id = 0

    def get_results(self) -> Dict[str, float]:
        if not self.assignments:
            return {"max_delay": float('inf'), "avg_delay": float('inf')}
        delays = [a.delay for a in self.assignments]
        return {
            "max_delay": max(delays),
            "avg_delay": sum(delays) / len(delays),
            "num_assigned": len(delays)
        }

## Cell 2 (code)

# 创建仿真
sim = SimulationEnvironment(seed=123)

# 生成 100 个 worker 和 100 个 request
sim.generate_synthetic_data(
    num_workers=100,
    num_requests=100,
    time_range=(0, 2000),
    space_range=(0, 1000),
    worker_time_dist="uniform",
    request_time_dist="uniform",
    loc_dist="uniform"
)



## Cell 3 (markdown)

下面是TBG（阈值贪心算法），请完成TODO 1-TODO 4缺失的部分以及finalize函数

## Cell 4 (code)

class TBGAlgorithm:
    def __init__(self, gamma: float):
        self.gamma = gamma
        self.available_workers = []          # List[Worker]：当前未分配的工作者
        self.buffered_requests = []         # List[Request]：缓冲的请求（按到达时间排序）
        self.current_time = 0.0
        self.assignments = []               # 用于记录结果

    def on_request_arrival(self, request: Request):
        """
        当新请求到达时调用
        """
        self.current_time = request.arrival_time
        
        # 检查是否有可用工作者，且距离 <= gamma
        assigned = False
        best_worker = None
        min_dist = float('inf')
        
        for w in self.available_workers:
            d = euclidean_distance(w.loc, request.loc)
            if d <= self.gamma and d < min_dist:
                min_dist = d
                best_worker = w
        
        if best_worker is not None:
            # TODO 1: 分配 best_worker 给 request
            # 记录 assignment（assign_time = current_time）
            # 从 available_workers 中移除 best_worker
            pass
        else:
            # TODO 2: 将 request 加入 buffered_requests
            pass

    def on_worker_arrival(self, worker: Worker):
        """
        当新工作者到达时调用
        """
        self.current_time = worker.arrival_time
        
        # 先检查是否有请求已超时（等待时间 >= gamma）
        candidate_request = None
        for r in self.buffered_requests:
            wait_time = self.current_time - r.arrival_time
            if wait_time >= self.gamma:
                candidate_request = r
                break  # 分配第一个超时的
        
        if candidate_request is not None:
            # TODO 3: 分配 worker 给 candidate_request
            # 从 buffered_requests 中移除 candidate_request
            # 不需要检查距离（必须分配！）
            pass
        else:
            # 尝试找一个总延迟 < gamma 的请求
            best_request = None
            min_total_delay = float('inf')
            
            for r in self.buffered_requests:
                travel_time = euclidean_distance(worker.loc, r.loc)
                total_delay = (self.current_time - r.arrival_time) + travel_time
                if total_delay < self.gamma and total_delay < min_total_delay:
                    min_total_delay = total_delay
                    best_request = r
            
            if best_request is not None:
                # TODO 4: 分配 worker 给 best_request
                # 从 buffered_requests 中移除 best_request
                pass
            else:
                # TODO 5: 将 worker 加入 available_workers
                pass

    def finalize(self, final_time: float):
        """
        仿真结束时调用：强制分配剩余请求
        """
        pass

## Cell 5 (markdown)

请结合仿真环境，调用class TBGAlgorithm:来验证，并做分析报告

## Cell 6 (code)

# 验证

## Cell 7 (markdown)

下面是BB算法(基于批次匹配),请你补全下面 # TODO 部分（创建 Assignment 对象并加入列表）。

## Cell 8 (code)

from scipy.optimize import linear_sum_assignment  # 这就是 KM 算法的最小权实现！

class BBAlgorithm:
    def __init__(self, theta: float):
        self.theta = theta
        self.buffered_workers = []   # List[Worker]
        self.buffered_requests = []  # List[Request]
        self.assignments = []
        self.next_batch_time = theta

    def on_worker_arrival(self, worker: Worker):
        # 直接加入缓冲区
        self.buffered_workers.append(worker)

    def on_request_arrival(self, request: Request):
        # 直接加入缓冲区
        self.buffered_requests.append(request)

    def _process_batch(self, batch_time: float):
        if not self.buffered_workers or not self.buffered_requests:
            self.buffered_workers.clear()
            self.buffered_requests.clear()
            return

        n = len(self.buffered_workers)
        m = len(self.buffered_requests)
        k = min(n, m)

        # Step 1: 构建延迟代价矩阵 C (n x m)
        C = np.zeros((n, m))
        for i, w in enumerate(self.buffered_workers):
            for j, r in enumerate(self.buffered_requests):
                wait = batch_time - r.arrival_time          # ≥0
                travel = euclidean_distance(w.loc, r.loc)   # ≥0
                C[i][j] = wait + travel                     # 这就是延迟！

        # Step 2: 补零/补齐为方阵（linear_sum_assignment 要求可矩形，但内部会处理）
        # 直接调用 KM（最小权匹配）
        row_ind, col_ind = linear_sum_assignment(C)

        # Step 3: 只取前 k 对有效匹配（避免越界）
        matched_pairs = []
        used_rows = set()
        used_cols = set()
        for i in range(len(row_ind)):
            wi = row_ind[i]
            rj = col_ind[i]
            if wi < n and rj < m and wi not in used_rows and rj not in used_cols:
                matched_pairs.append((wi, rj))
                used_rows.add(wi)
                used_cols.add(rj)
                if len(matched_pairs) == k:
                    break

        # TODO: 根据 matched_pairs 创建 Assignment 对象
        # assign_time = batch_time
        # delay = C[wi][rj]
        for wi, rj in matched_pairs:
            w = self.buffered_workers[wi]
            r = self.buffered_requests[rj]
            delay = C[wi, rj]
            self.assignments.append(Assignment(
                worker_id=w.id,
                request_id=r.id,
                assign_time=batch_time,
                delay=delay
            ))

        # 清空缓冲区（简单策略：未匹配的直接丢弃）
        self.buffered_workers.clear()
        self.buffered_requests.clear()

    def advance_to_time(self, current_time: float):
        """由仿真器调用：推进到 current_time，触发所有到期的批处理"""
        while self.next_batch_time <= current_time:
            self._process_batch(self.next_batch_time)
            self.next_batch_time += self.theta

## Cell 9 (markdown)

使用之前构建的 SimulationEnvironment 生成数据，运行 BB 算法。

## Cell 10 (markdown)

可以尝试不同批次大小 theta = 50, 100, 200，记录 max_delay 和 avg_delay

## Cell 11 (markdown)

验证实验

## Cell 12 (code)

# 验证

## Cell 13 (markdown)

采用NSGA2，探索联合优化最小化接客距离与最大化平台收入（用送客距离表示）的帕累托前沿，并对比竞争比


## Cell 14 (code)

# 代码，请自己写
