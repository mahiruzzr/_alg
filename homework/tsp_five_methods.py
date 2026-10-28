"""
旅行推銷員問題 (TSP):五種解法比較
  1. 改良法 (2-opt 全域掃描改良)
  2. 爬山演算法 (Hill Climbing)
  3. 模擬退火法 (Simulated Annealing)
  4. 梯度下降法 (Elastic Net:對能量函數做梯度下降)
  5. 貪婪演算法 (最近鄰居法)

只需要 numpy;若有安裝 matplotlib 會另外輸出比較圖 tsp_result.png
執行:python tsp_five_methods.py [城市數量] [隨機種子]
"""
import math
import random
import sys
import time

import numpy as np


# ---------------------------------------------------------------- 基本工具
def make_cities(n, seed):
    rng = np.random.default_rng(seed)
    return rng.random((n, 2)) * 100


def dist_matrix(pts):
    diff = pts[:, None, :] - pts[None, :, :]
    return np.sqrt((diff ** 2).sum(-1))


def tour_length(tour, D):
    t = np.asarray(tour)
    return float(D[t, np.roll(t, -1)].sum())


def reversal_delta(tour, i, j, D):
    """把 tour[i..j] 反轉後,總長度的變化量 (O(1) 計算)。要求 1 <= i < j <= n-1"""
    n = len(tour)
    a, b = tour[i - 1], tour[i]
    c, d = tour[j], tour[(j + 1) % n]
    return D[a, c] + D[b, d] - D[a, b] - D[c, d]


def apply_reversal(tour, i, j):
    tour[i:j + 1] = tour[i:j + 1][::-1]


# ---------------------------------------------------------------- 5. 貪婪演算法
def greedy_nearest_neighbor(D, start=0):
    """每一步都走向「尚未拜訪、距離目前城市最近」的城市。"""
    n = len(D)
    visited = [False] * n
    tour = [start]
    visited[start] = True
    for _ in range(n - 1):
        cur = tour[-1]
        nxt = min((c for c in range(n) if not visited[c]), key=lambda c: D[cur, c])
        tour.append(nxt)
        visited[nxt] = True
    return tour


# ---------------------------------------------------------------- 1. 改良法 (2-opt)
def improvement_2opt(D, init_tour):
    """
    從一條初始路徑出發,反覆掃描所有「兩邊交換 (2-opt)」,
    只要能縮短總長度就採用,直到整條路徑再也找不到可改良的交換為止。
    """
    n = len(D)
    tour = list(init_tour)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if reversal_delta(tour, i, j, D) < -1e-9:
                    apply_reversal(tour, i, j)
                    improved = True
    return tour


# ---------------------------------------------------------------- 2. 爬山演算法
def hill_climbing(D, init_tour, max_iter=200_000, seed=0):
    """
    隨機挑一個鄰居 (反轉一段路徑),只接受「更短」的解;
    不接受變差的解,所以會卡在局部最佳解。
    """
    rnd = random.Random(seed)
    n = len(D)
    tour = list(init_tour)
    for _ in range(max_iter):
        i = rnd.randint(1, n - 2)
        j = rnd.randint(i + 1, n - 1)
        if reversal_delta(tour, i, j, D) < -1e-9:
            apply_reversal(tour, i, j)
    return tour


# ---------------------------------------------------------------- 3. 模擬退火法
def simulated_annealing(D, init_tour, T0=100.0, T_min=1e-3, alpha=0.995,
                        moves_per_temp=100, seed=0):
    """
    與爬山法使用相同的鄰居,差別只在接受準則:
    變差的解也以機率 exp(-Δ/T) 接受,溫度 T 逐步下降,
    前期能跳出局部最佳解,後期趨近爬山法。
    """
    rnd = random.Random(seed)
    n = len(D)
    tour = list(init_tour)
    cur_len = tour_length(tour, D)
    best, best_len = tour[:], cur_len
    T = T0
    while T > T_min:
        for _ in range(moves_per_temp):
            i = rnd.randint(1, n - 2)
            j = rnd.randint(i + 1, n - 1)
            delta = reversal_delta(tour, i, j, D)
            if delta < 0 or rnd.random() < math.exp(-delta / T):
                apply_reversal(tour, i, j)
                cur_len += delta
                if cur_len < best_len - 1e-9:
                    best, best_len = tour[:], cur_len
        T *= alpha
    return best


# ---------------------------------------------------------------- 4. 梯度下降法
def elastic_net_gradient_descent(pts, iters=8000, alpha=0.2, beta=2.0,
                                 K0=0.2, K_min=0.01, seed=0):
    """
    TSP 是離散問題,沒辦法直接對「路徑」微分。常見做法是 Elastic Net (Durbin & Willshaw):
    放一條由 m 個節點 y_j 組成的彈性環,定義連續的能量函數

        E = -alpha*K * Σ_i ln Σ_j exp(-|x_i - y_j|² / 2K²)  +  (beta/2) * Σ_j |y_{j+1} - y_j|²

    第一項把環拉向城市 x_i,第二項讓環保持短而平滑。
    每次迭代沿 -∇E 方向更新 y_j (梯度下降),同時逐步縮小 K 讓環越來越貼近城市。
    最後依每個城市最接近的環節點順序,讀出拜訪順序。
    """
    n = len(pts)
    m = int(2.5 * n)
    x = (pts - pts.min(0)) / (pts.max(0) - pts.min(0)).max()   # 正規化到單位正方形
    theta = np.linspace(0, 2 * np.pi, m, endpoint=False)
    y = x.mean(0) + 0.1 * np.c_[np.cos(theta), np.sin(theta)]
    K = K0
    for t in range(iters):
        d2 = ((x[:, None, :] - y[None, :, :]) ** 2).sum(-1)          # n × m
        w = np.exp(-(d2 - d2.min(1, keepdims=True)) / (2 * K * K))   # 數值穩定
        w /= w.sum(1, keepdims=True)                                 # 城市 i 對節點 j 的權重
        pull = alpha * (w[:, :, None] * (x[:, None, :] - y[None, :, :])).sum(0)
        tension = beta * K * (np.roll(y, -1, 0) - 2 * y + np.roll(y, 1, 0))
        y += pull + tension                                          # 梯度下降一步
        if (t + 1) % 25 == 0:
            K = max(K_min, K * 0.99)
    d2 = ((x[:, None, :] - y[None, :, :]) ** 2).sum(-1)
    pos = d2.argmin(1)                                               # 每個城市對應的環上位置
    order = list(np.argsort(pos, kind="stable"))
    k = order.index(0)
    return order[k:] + order[:k]                                     # 旋轉成從城市 0 出發


# ---------------------------------------------------------------- 主程式
def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    pts = make_cities(n, seed)
    D = dist_matrix(pts)

    rnd = random.Random(seed)
    random_tour = [0] + rnd.sample(range(1, n), n - 1)   # 共同的隨機起始路徑

    runs = [
        ("1. 改良法 (2-opt)",      lambda: improvement_2opt(D, random_tour)),
        ("2. 爬山演算法",          lambda: hill_climbing(D, random_tour, seed=seed)),
        ("3. 模擬退火法",          lambda: simulated_annealing(D, random_tour, seed=seed)),
        ("4. 梯度下降法 (彈性網)",  lambda: elastic_net_gradient_descent(pts, seed=seed)),
        ("5. 貪婪演算法 (最近鄰)",  lambda: greedy_nearest_neighbor(D)),
    ]

    print(f"城市數量 n = {n},隨機種子 = {seed}")
    print(f"隨機路徑長度 (起始解) = {tour_length(random_tour, D):.2f}\n")
    results = []
    for name, fn in runs:
        t0 = time.time()
        tour = [int(c) for c in fn()]
        assert sorted(tour) == list(range(n)), f"{name} 產生的不是合法路徑"
        L = tour_length(tour, D)
        results.append((name, tour, L))
        print(f"{name:<18} 長度 = {L:8.2f}   耗時 = {time.time() - t0:6.2f}s")
        print(f"    路徑: {tour}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Noto Sans CJK TC", "Noto Sans CJK JP",
                                           "Microsoft JhengHei", "PingFang TC",
                                           "Arial Unicode MS", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        fig, axes = plt.subplots(2, 3, figsize=(15, 9))
        for ax, (name, tour, L) in zip(axes.flat, results):
            p = pts[tour + [tour[0]]]
            ax.plot(p[:, 0], p[:, 1], "-o", ms=4, lw=1.2)
            ax.plot(*pts[tour[0]], "r*", ms=14)
            ax.set_title(f"{name}\n長度 = {L:.1f}")
            ax.set_aspect("equal")
        axes.flat[-1].axis("off")
        plt.tight_layout()
        plt.savefig("tsp_result.png", dpi=130)
        print("\n已輸出比較圖 tsp_result.png")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
