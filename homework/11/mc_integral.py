"""
第 6 題：蒙地卡羅法多變數積分模組 (Monte Carlo Hypervolume Integration)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫與最佳化。
This code was designed, implemented, and optimized with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================

題目需求：
6. 改用蒙地卡羅法做 n 變數積分，題目同上一題
    * 分別用 1 維, 2 維, 5 維, 100 維來計算
    * 範例用 f(x) = x_1^2 + ... + x_n^2 , low=0, high=1
"""

from typing import Callable, Sequence, Union, Tuple, Optional
import numpy as np


def mc_integral(
    f: Callable[[np.ndarray], Union[float, np.ndarray]],
    low: Union[Sequence[float], np.ndarray],
    high: Union[Sequence[float], np.ndarray],
    n_samples: int = 200_000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    使用蒙地卡羅法 (Monte Carlo Integration) 計算 n 變數超體積積分。

    數學原理:
        I = int_{Omega} f(x) dx ≈ V * (1 / N) * sum_{i=1}^N f(X_i)
        其中 Omega = [low_1, high_1] x ... x [low_n, high_n]
        體積 V = prod_{d=1}^n (high_d - low_d)
        隨機向量 X_i ~ Uniform(low, high)
        大數法則保證當 N -> inf 時收斂至真實值。
        中心極限定理保證收斂速度為 O(1 / sqrt(N))，其誤差「與維度 n 無關」！
        這使其成為克服「維度災難」計算高維超體積積分的最佳利器。

    參數:
        f: 被積函數 f(x)，可接收 (n,) 向量或 (N, n) 批次矩陣
        low: 各維度積分下限陣列
        high: 各維度積分上限陣列
        n_samples: 隨機採樣數量 N (預設 200,000)
        seed: 隨機數種子 (選填，方便結果重現)

    回傳:
        (估計值, 標準誤 Standard Error)
    """
    low_arr = np.asarray(low, dtype=float)
    high_arr = np.asarray(high, dtype=float)

    if low_arr.ndim == 0:
        low_arr = np.array([low_arr])
    if high_arr.ndim == 0:
        high_arr = np.array([high_arr])

    n = len(low_arr)
    if len(high_arr) != n:
        raise ValueError(f"low (長度 {n}) 與 high (長度 {len(high_arr)}) 維度不符")

    if np.any(high_arr < low_arr):
        raise ValueError("積分上限 high 的所有分量必須大於或等於下限 low")

    if n_samples <= 0:
        raise ValueError("隨機採樣數量 n_samples 必須大於 0")

    # 超長方體總體積 V = (high_1 - low_1) * ... * (high_n - low_n)
    side_lengths = high_arr - low_arr
    V = float(np.prod(side_lengths))

    # 生成均勻分布的隨機取樣點，形狀為 (n_samples, n)
    rng = np.random.default_rng(seed)
    random_samples = rng.uniform(low_arr, high_arr, size=(n_samples, n))

    # 評估函數值 (優先使用向量化加速，若不支援則使用逐點迴圈)
    try:
        values = f(random_samples)
        if not isinstance(values, np.ndarray) or values.shape != (n_samples,):
            # 若不是回傳長度為 N 的 1D array，改用逐點評估
            values = np.array([f(pt) for pt in random_samples], dtype=float)
    except Exception:
        values = np.array([f(pt) for pt in random_samples], dtype=float)

    # 蒙地卡羅積分估計
    mean_f = float(np.mean(values))
    integral_val = V * mean_f

    # 計算統計標準誤 Standard Error: SE = V * sigma / sqrt(N)
    std_f = float(np.std(values, ddof=1)) if n_samples > 1 else 0.0
    standard_error = V * (std_f / np.sqrt(n_samples))

    return integral_val, standard_error


def run_mc_benchmark():
    """
    執行第 6 題的要求：
    使用蒙地卡羅法分別計算 1 維, 2 維, 5 維, 100 維的 f(x) = sum(x_i^2), low=0, high=1
    """
    import time

    print("=" * 70)
    print("第 6 題：蒙地卡羅法 mc_integral(f, low, high) 基準測試")
    print("被積函數: f(x) = x_1^2 + x_2^2 + ... + x_n^2, 範圍: [0, 1]^n")
    print("理論解析解: int_0^1 ... int_0^1 (sum x_i^2) dx = n / 3")
    print("=" * 70)

    dimensions = [1, 2, 5, 100]
    n_samples = 300_000

    for n in dimensions:
        low = np.zeros(n)
        high = np.ones(n)
        exact_value = n / 3.0

        # 定義被積函數 f(x)，支援向量化評估 (axis=-1)
        # 若傳入 shape=(N, n)，則回傳 shape=(N,)
        def f(x: np.ndarray) -> np.ndarray:
            if x.ndim == 1:
                return float(np.sum(x**2))
            return np.sum(x**2, axis=-1)

        print(f"\n--- [維度 n = {n}] ---")
        print(f"理論解析解: {n}/3 = {exact_value:.6f}")

        start_time = time.perf_counter()
        val, se = mc_integral(f, low, high, n_samples=n_samples, seed=42)
        elapsed = time.perf_counter() - start_time
        error = abs(val - exact_value)

        print(f"蒙地卡羅估計: {val:.6f} ± {se:.6f} (95% 信心區間約 [{val - 1.96*se:.6f}, {val + 1.96*se:.6f}])")
        print(f"絕對誤差:     {error:.6f}")
        print(f"誤差在 SE 內: {error <= se} (在 2*SE 內: {error <= 2*se})")
        print(f"執行耗時:     {elapsed:.4f} 秒 (採樣數 N = {n_samples:,})")


if __name__ == "__main__":
    run_mc_benchmark()
