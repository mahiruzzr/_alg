"""
單變數數值微積分與蒙地卡羅積分模組 (Single-Variable Numerical Calculus & Monte Carlo)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫與最佳化。
This code was designed, implemented, and optimized with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================

包含題目：
1. 數值方法計算單變數微分與積分
2. 蒙地卡羅法計算單變數積分
"""

from typing import Callable, Literal, Tuple, Optional
import numpy as np


def numerical_diff_1d(
    f: Callable[[float], float],
    x: float,
    h: float = 1e-6,
    method: Literal["central", "forward", "backward"] = "central"
) -> float:
    """
    使用有限差分法計算單變數函數 f 在 x 點的一階導數 (數值微分)。

    參數:
        f: 單變數目標函數 f(x)
        x: 評估導數的位置
        h: 步長 (微小增量，預設 1e-6)
        method: 差分方法，可選:
            - 'central': 中心差分法 (預設，截斷誤差 O(h^2))
            - 'forward': 前向差分法 (截斷誤差 O(h))
            - 'backward': 後向差分法 (截斷誤差 O(h))

    回傳:
        f'(x) 的數值估計值
    """
    if h <= 0:
        raise ValueError("步長 h 必須大於 0")

    if method == "central":
        # 中心差分公式: (f(x + h) - f(x - h)) / (2 * h)
        return (f(x + h) - f(x - h)) / (2.0 * h)
    elif method == "forward":
        # 前向差分公式: (f(x + h) - f(x)) / h
        return (f(x + h) - f(x)) / h
    elif method == "backward":
        # 後向差分公式: (f(x) - f(x - h)) / h
        return (f(x) - f(x - h)) / h
    else:
        raise ValueError(f"不支援的差分方法: {method}，請選擇 'central', 'forward' 或 'backward'")


def numerical_integral_1d(
    f: Callable[[float], float],
    a: float,
    b: float,
    n_steps: int = 1000,
    method: Literal["trapezoid", "simpson", "midpoint"] = "simpson"
) -> float:
    """
    使用數值積分法計算單變數定積分 int_a^b f(x) dx。

    參數:
        f: 單變數目標函數 f(x)
        a: 積分下限
        b: 積分上限
        n_steps: 切分區間數量 (預設 1000)
        method: 積分方法，可選:
            - 'simpson': 辛普森法 (Simpson's 1/3 rule, 截斷誤差 O(h^4), 預設)
            - 'trapezoid': 梯形法 (Trapezoidal rule, 截斷誤差 O(h^2))
            - 'midpoint': 中點黎曼和 (Midpoint rule, 截斷誤差 O(h^2))

    回傳:
        定積分數值估計值
    """
    if n_steps <= 0:
        raise ValueError("切分步數 n_steps 必須為正整數")
    if a == b:
        return 0.0

    # 處理積分下限大於上限的情況: int_a^b f(x)dx = - int_b^a f(x)dx
    if a > b:
        return -numerical_integral_1d(f, b, a, n_steps=n_steps, method=method)

    h = (b - a) / n_steps

    if method == "midpoint":
        # 中點法: sum(f(a + (i + 0.5) * h)) * h
        i_values = np.arange(n_steps)
        midpoints = a + (i_values + 0.5) * h
        values = np.array([f(float(m)) for m in midpoints])
        return float(np.sum(values) * h)

    elif method == "trapezoid":
        # 梯形法: (h / 2) * [f(a) + 2 * sum(f(x_i)) + f(b)]
        x_values = np.linspace(a, b, n_steps + 1)
        y_values = np.array([f(float(x)) for x in x_values])
        return float((h / 2.0) * (y_values[0] + 2.0 * np.sum(y_values[1:-1]) + y_values[-1]))

    elif method == "simpson":
        # 辛普森 1/3 法 (需偶數個區間，若為奇數則調整為偶數)
        if n_steps % 2 != 0:
            n_steps += 1
            h = (b - a) / n_steps

        x_values = np.linspace(a, b, n_steps + 1)
        y_values = np.array([f(float(x)) for x in x_values])

        # Simpson 公式: (h / 3) * [y_0 + 4 * sum(奇數項) + 2 * sum(偶數項) + y_n]
        odd_sum = np.sum(y_values[1:-1:2])
        even_sum = np.sum(y_values[2:-1:2])
        total = y_values[0] + 4.0 * odd_sum + 2.0 * even_sum + y_values[-1]
        return float((h / 3.0) * total)

    else:
        raise ValueError(f"不支援的積分方法: {method}，請選擇 'simpson', 'trapezoid' 或 'midpoint'")


def monte_carlo_integral_1d(
    f: Callable[[float], float],
    a: float,
    b: float,
    n_samples: int = 100_000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    使用蒙地卡羅法計算單變數定積分 int_a^b f(x) dx。

    公式:
        I ≈ (b - a) * (1 / N) * sum_{i=1}^N f(X_i), 其中 X_i ~ Uniform(a, b)
        標準誤 (Standard Error) = (b - a) * std(f(X)) / sqrt(N)

    參數:
        f: 單變數目標函數 f(x)
        a: 積分下限
        b: 積分上限
        n_samples: 蒙地卡羅隨機抽樣數量 (預設 100,000)
        seed: 隨機數種子 (方便重現測試)

    回傳:
        (估計值, 標準誤)
    """
    if n_samples <= 0:
        raise ValueError("抽樣數量 n_samples 必須為正整數")
    if a == b:
        return 0.0, 0.0

    sign = 1.0
    if a > b:
        a, b = b, a
        sign = -1.0

    rng = np.random.default_rng(seed)
    random_points = rng.uniform(a, b, size=n_samples)

    # 評估函數值
    evaluated_values = np.vectorize(f, otypes=[float])(random_points)

    mean_value = float(np.mean(evaluated_values))
    interval_length = b - a
    estimate = sign * interval_length * mean_value

    # 計算估計的標準誤 (Standard Error)
    sample_std = float(np.std(evaluated_values, ddof=1)) if n_samples > 1 else 0.0
    standard_error = interval_length * (sample_std / np.sqrt(n_samples))

    return estimate, standard_error


if __name__ == "__main__":
    import math

    print("=== 單變數數值微積分與蒙地卡羅積分測試 ===")
    
    # 測試函數 1: f(x) = x^3 + 2x^2 + 5, f'(2) = 3*(4) + 4*(2) = 20
    f1 = lambda x: x**3 + 2.0 * x**2 + 5.0
    print("\n[測試 1] 微分: f(x) = x^3 + 2x^2 + 5 在 x = 2 的導數")
    print(f"  解析解: 20.0")
    print(f"  中心差分 (h=1e-6): {numerical_diff_1d(f1, 2.0, method='central'):.8f}")
    print(f"  前向差分 (h=1e-6): {numerical_diff_1d(f1, 2.0, method='forward'):.8f}")

    # 測試函數 2: f(x) = sin(x), f'(pi/3) = cos(pi/3) = 0.5
    f2 = math.sin
    print("\n[測試 2] 微分: f(x) = sin(x) 在 x = pi/3 的導數")
    print(f"  解析解: {math.cos(math.pi / 3):.8f}")
    print(f"  中心差分: {numerical_diff_1d(f2, math.pi / 3):.8f}")

    # 測試函數 3: 積分 f(x) = x^2 從 0 到 1, 解析解 = 1/3 ≈ 0.33333333
    f3 = lambda x: x**2
    print("\n[測試 3] 數值積分: f(x) = x^2, [0, 1]")
    print(f"  解析解: 1/3 ≈ {1.0 / 3.0:.8f}")
    print(f"  辛普森法 (n=1000):   {numerical_integral_1d(f3, 0.0, 1.0, method='simpson'):.8f}")
    print(f"  梯形法   (n=1000):   {numerical_integral_1d(f3, 0.0, 1.0, method='trapezoid'):.8f}")
    print(f"  中點法   (n=1000):   {numerical_integral_1d(f3, 0.0, 1.0, method='midpoint'):.8f}")

    # 測試函數 4: 蒙地卡羅積分 f(x) = x^2, [0, 1]
    print("\n[測試 4] 蒙地卡羅積分: f(x) = x^2, [0, 1] (N=100,000)")
    mc_val, mc_err = monte_carlo_integral_1d(f3, 0.0, 1.0, n_samples=100_000, seed=42)
    print(f"  解析解: 1/3 ≈ {1.0 / 3.0:.8f}")
    print(f"  蒙地卡羅估計: {mc_val:.8f} ± {mc_err:.8f}")
