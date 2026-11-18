"""
多變數數值微積分與蒙地卡羅超體積積分模組 (Multivariable Calculus & Hypervolume Integration)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫與最佳化。
This code was designed, implemented, and optimized with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================

包含題目：
3. 數值方法計算 n 變數微分 (梯度 Gradient) 與積分 (超體積 Hypervolume)
4. 蒙地卡羅法計算 n 變數積分 (超體積 Hypervolume)
"""

from typing import Callable, Sequence, Union, Tuple, Optional
import itertools
import numpy as np


def numerical_gradient(
    f: Callable[[np.ndarray], float],
    x: Union[Sequence[float], np.ndarray],
    h: float = 1e-6
) -> np.ndarray:
    """
    使用中心差分法計算多變數純量函數 f 在點 x 的數值梯度 (Numerical Gradient)。

    公式:
        grad(f)(x) = [df/dx_1, df/dx_2, ..., df/dx_n]^T
        其中 df/dx_i ≈ (f(x + h * e_i) - f(x - h * e_i)) / (2 * h)

    參數:
        f: 接受長度為 n 的一維陣列並回傳純量 float 的函數 f(x)
        x: 評估梯度的位置 (長度為 n 的序列或陣列)
        h: 差分步長 (預設 1e-6)

    回傳:
        長度為 n 的梯度向量 (numpy.ndarray)
    """
    x_arr = np.array(x, dtype=float)
    n = len(x_arr)
    grad = np.zeros(n, dtype=float)

    for i in range(n):
        # 建立微小偏量向量 h * e_i
        x_plus = x_arr.copy()
        x_minus = x_arr.copy()
        x_plus[i] += h
        x_minus[i] -= h

        # 數值偏導數 (中心差分)
        grad[i] = (f(x_plus) - f(x_minus)) / (2.0 * h)

    return grad


def numerical_integral_nd(
    f: Callable[[np.ndarray], float],
    low: Union[Sequence[float], np.ndarray],
    high: Union[Sequence[float], np.ndarray],
    steps_per_dim: int = 10,
    max_evaluations: int = 2_000_000
) -> float:
    """
    使用中點黎曼網格法計算多變數在超長方體上的定積分 (超體積積分)。

    參數:
        f: 多變數函數 f(x)，接收長度為 n 的 1D 陣列
        low: 各維度積分下限 [low_1, low_2, ..., low_n]
        high: 各維度積分上限 [high_1, high_2, ..., high_n]
        steps_per_dim: 每個維度的切分步數 (預設 10)
        max_evaluations: 最大允許計算點數 (避免高維時記憶體爆掉或卡死)

    回傳:
        超體積積分數值估計值
    """
    low_arr = np.array(low, dtype=float)
    high_arr = np.array(high, dtype=float)
    n = len(low_arr)

    if len(high_arr) != n:
        raise ValueError(f"low (長度 {n}) 與 high (長度 {len(high_arr)}) 維度不一致")

    if steps_per_dim <= 0:
        raise ValueError("steps_per_dim 必須大於 0")

    # 檢查總評估點數: steps_per_dim ^ n
    total_points = steps_per_dim ** n
    if total_points > max_evaluations:
        raise OverflowError(
            f"維度災難警告: 維度 n={n} 且 steps_per_dim={steps_per_dim}，"
            f"總評估點數高達 {total_points:.2e}，超過安全上限 {max_evaluations}。"
            f"請降低步數或改用蒙地卡羅積分法。"
        )

    # 計算各維度的網格寬度 dx_i 與中點
    dx = (high_arr - low_arr) / steps_per_dim
    dV = float(np.prod(dx))  # 超體積微元 dV = dx_1 * dx_2 * ... * dx_n

    # 生成各軸中點序列
    dim_midpoints = [
        low_arr[d] + (np.arange(steps_per_dim) + 0.5) * dx[d]
        for d in range(n)
    ]

    # 利用 itertools.product 遍歷 n 維網格中點
    total_sum = 0.0
    for pt in itertools.product(*dim_midpoints):
        total_sum += f(np.array(pt))

    return float(total_sum * dV)


def monte_carlo_integral_nd(
    f: Callable[[np.ndarray], float],
    low: Union[Sequence[float], np.ndarray],
    high: Union[Sequence[float], np.ndarray],
    n_samples: int = 100_000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    使用蒙地卡羅法計算 n 變數在超長方體上的定積分 (超體積)。

    公式:
        I ≈ V * (1 / N) * sum_{i=1}^N f(X_i)
        其中 V = prod_{i=1}^n (high_i - low_i)
        X_i 為在 [low, high] 上的均勻隨機向量 ~ Uniform(low, high)
        標準誤 (Standard Error) = V * std(f(X)) / sqrt(N)

    參數:
        f: 多變數目標函數 f(x)
        low: 各維度積分下限 [low_1, ..., low_n]
        high: 各維度積分上限 [high_1, ..., high_n]
        n_samples: 隨機取樣點數量 (預設 100,000)
        seed: 隨機數種子 (方便重現)

    回傳:
        (積分估計值, 標準誤)
    """
    low_arr = np.array(low, dtype=float)
    high_arr = np.array(high, dtype=float)
    n = len(low_arr)

    if len(high_arr) != n:
        raise ValueError(f"low (長度 {n}) 與 high (長度 {len(high_arr)}) 維度不一致")
    if n_samples <= 0:
        raise ValueError("抽樣數量 n_samples 必須大於 0")

    # 計算超立方體總體積 V
    edge_lengths = high_arr - low_arr
    hypervolume = float(np.prod(edge_lengths))

    rng = np.random.default_rng(seed)
    # 產生 shape = (n_samples, n) 的均勻分布隨機點
    random_points = rng.uniform(low_arr, high_arr, size=(n_samples, n))

    # 嘗試向量化計算以取得最高效能；若不支援則以列表推導回退
    try:
        sample_values = f(random_points)
        if not isinstance(sample_values, np.ndarray) or sample_values.shape != (n_samples,):
            sample_values = np.array([f(pt) for pt in random_points], dtype=float)
    except Exception:
        sample_values = np.array([f(pt) for pt in random_points], dtype=float)

    mean_val = float(np.mean(sample_values))
    estimate = hypervolume * mean_val

    sample_std = float(np.std(sample_values, ddof=1)) if n_samples > 1 else 0.0
    standard_error = hypervolume * (sample_std / np.sqrt(n_samples))

    return estimate, standard_error


if __name__ == "__main__":
    print("=== 多變數數值微積分與蒙地卡羅超體積測試 ===")

    # 測試 1: 梯度計算 f(x, y, z) = x^2 + 3*y^2 + 2*z^3
    # 梯度解析解: [2x, 6y, 6z^2]
    # 在 (1, 2, 3) 處: [2, 12, 54]
    f_grad_test = lambda x: x[0]**2 + 3.0 * x[1]**2 + 2.0 * x[2]**3
    x_test = [1.0, 2.0, 3.0]
    grad_num = numerical_gradient(f_grad_test, x_test)
    grad_exact = np.array([2.0, 12.0, 54.0])
    print("\n[測試 1] 多變數梯度: f(x, y, z) = x^2 + 3y^2 + 2z^3 在 (1, 2, 3)")
    print(f"  解析解: {grad_exact}")
    print(f"  數值梯度: {grad_num}")
    print(f"  誤差: {np.max(np.abs(grad_num - grad_exact)):.2e}")

    # 測試 2: 2 變數超體積積分: f(x, y) = x * y 在 [0, 2] x [0, 3]
    # 解析解: (int_0^2 x dx) * (int_0^3 y dy) = (2) * (4.5) = 9.0
    f_2d = lambda x: x[0] * x[1]
    low_2d = [0.0, 0.0]
    high_2d = [2.0, 3.0]
    val_num_2d = numerical_integral_nd(f_2d, low_2d, high_2d, steps_per_dim=100)
    print("\n[測試 2] 2變數數值超體積積分: f(x,y)=x*y, [0,2]x[0,3]")
    print(f"  解析解: 9.0")
    print(f"  數值積分: {val_num_2d:.6f}")

    # 測試 3: 3 變數球體體積 (指示函數蒙地卡羅積分)
    # 半徑 R = 1 的球體體積: 4/3 * pi * 1^3 ≈ 4.18879
    # 積分範圍: [-1, 1]^3, 超立方體體積 = 8
    # 若 x^2 + y^2 + z^2 <= 1 則 f(x) = 1，否則 0
    sphere_indicator = lambda x: 1.0 if np.sum(x**2) <= 1.0 else 0.0
    sphere_vol, sphere_err = monte_carlo_integral_nd(
        sphere_indicator,
        low=[-1.0, -1.0, -1.0],
        high=[1.0, 1.0, 1.0],
        n_samples=200_000,
        seed=42
    )
    exact_sphere = (4.0 / 3.0) * np.pi
    print("\n[測試 3] 3變數蒙地卡羅積分: 計算半徑為 1 的球體體積")
    print(f"  解析解 (4/3*pi): {exact_sphere:.6f}")
    print(f"  蒙地卡羅估計:   {sphere_vol:.6f} ± {sphere_err:.6f}")
