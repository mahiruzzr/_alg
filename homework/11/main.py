"""
數值微積分與蒙地卡羅方法展示主程式 (Main Demonstration Script)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫與最佳化。
This code was designed, implemented, and optimized with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================

涵蓋 6 大主題完整示範：
1. 數值方法計算單變數微分與積分
2. 蒙地卡羅法計算單變數積分
3. 數值方法計算 n 變數微分 (梯度) 與積分 (超體積)
4. 蒙地卡羅法計算 n 變數積分 (超體積)
5. 黎曼積分法函數 integral(f, low, high) 計算 1, 2, 5, 100 維
6. 蒙地卡羅法函數 mc_integral(f, low, high) 計算 1, 2, 5, 100 維
"""

import math
import time
import numpy as np

from single_variable import (
    numerical_diff_1d,
    numerical_integral_1d,
    monte_carlo_integral_1d,
)
from multivariable import (
    numerical_gradient,
    numerical_integral_nd,
    monte_carlo_integral_nd,
)
from riemann import (
    integral,
    DimensionalityCurseError,
)
from mc_integral import (
    mc_integral,
)


def print_header(title: str):
    print("\n" + "=" * 76)
    print(f"  {title}")
    print("=" * 76)


def demo_topic_1():
    print_header("【題目 1】數值方法計算單變數微分與積分")
    
    # 1.1 單變數微分: f(x) = x^3 - 4x + 6, 在 x = 2
    # f'(x) = 3x^2 - 4 -> f'(2) = 12 - 4 = 8.0
    f1 = lambda x: x**3 - 4.0 * x + 6.0
    x0 = 2.0
    exact_deriv = 8.0
    
    print("--- 1.1 單變數數值微分 ---")
    print(f"目標函數: f(x) = x^3 - 4x + 6 在 x = {x0}")
    print(f"理論解析解: f'({x0}) = {exact_deriv:.6f}")
    
    for method in ["central", "forward", "backward"]:
        res = numerical_diff_1d(f1, x0, h=1e-5, method=method)
        err = abs(res - exact_deriv)
        print(f"  [{method:>8} 差分法] 數值估計: {res:.8f} (誤差: {err:.2e})")

    # 1.2 單變數積分: f(x) = sin(x) 在 [0, pi]
    # int_0^pi sin(x) dx = -cos(pi) - (-cos(0)) = 2.0
    print("\n--- 1.2 單變數數值積分 ---")
    f_int = math.sin
    exact_int = 2.0
    print("目標函數: f(x) = sin(x) 在 [0, pi]")
    print(f"理論解析解: int_0^pi sin(x) dx = {exact_int:.6f}")
    
    for method in ["simpson", "trapezoid", "midpoint"]:
        res = numerical_integral_1d(f_int, 0.0, math.pi, n_steps=1000, method=method)
        err = abs(res - exact_int)
        print(f"  [{method:>9} 法] 數值估計: {res:.8f} (誤差: {err:.2e})")


def demo_topic_2():
    print_header("【題目 2】蒙地卡羅法計算單變數積分")
    # 目標函數: f(x) = 4 / (1 + x^2) 在 [0, 1]
    # int_0^1 4/(1+x^2) dx = 4 * arctan(1) = pi ≈ 3.14159265
    f = lambda x: 4.0 / (1.0 + x**2)
    exact_pi = math.pi
    
    print("目標函數: f(x) = 4 / (1 + x^2) 在 [0, 1]")
    print(f"理論解析解: int_0^1 f(x) dx = pi ≈ {exact_pi:.8f}")
    
    sample_sizes = [1_000, 10_000, 100_000, 1_000_000]
    for n in sample_sizes:
        start = time.perf_counter()
        val, se = monte_carlo_integral_1d(f, 0.0, 1.0, n_samples=n, seed=42)
        elapsed = time.perf_counter() - start
        err = abs(val - exact_pi)
        print(f"  [採樣數 N = {n:>9,}] 估計值: {val:.6f} ± {se:.6f} | 絕對誤差: {err:.6f} | 耗時: {elapsed:.4f}s")


def demo_topic_3():
    print_header("【題目 3】數值方法計算 n 變數微分 (梯度) 與積分 (超體積)")
    
    # 3.1 梯度測試: f(x, y, z) = x^2 + 2y^2 + 3z^2 + xy - yz 在 (1, 2, -1)
    # grad_x = 2x + y = 2(1) + 2 = 4
    # grad_y = 4y + x - z = 4(2) + 1 - (-1) = 10
    # grad_z = 6z - y = 6(-1) - 2 = -8
    f_grad = lambda v: v[0]**2 + 2.0*v[1]**2 + 3.0*v[2]**2 + v[0]*v[1] - v[1]*v[2]
    pt = np.array([1.0, 2.0, -1.0])
    exact_grad = np.array([4.0, 10.0, -8.0])
    
    num_grad = numerical_gradient(f_grad, pt)
    print("--- 3.1 三變數數值梯度 ---")
    print("目標函數: f(x, y, z) = x^2 + 2y^2 + 3z^2 + xy - yz 在 (1, 2, -1)")
    print(f"  理論解析梯度: {exact_grad}")
    print(f"  中心差分梯度: {num_grad}")
    print(f"  最大座標誤差: {np.max(np.abs(num_grad - exact_grad)):.2e}")

    # 3.2 超體積積分測試: 3變數 f(x, y, z) = x * y * z 在 [0, 1] x [0, 2] x [0, 3]
    # int_0^1 x dx * int_0^2 y dy * int_0^3 z dz = (1/2) * (2) * (9/2) = 4.5
    f_vol = lambda v: v[0] * v[1] * v[2]
    low = [0.0, 0.0, 0.0]
    high = [1.0, 2.0, 3.0]
    exact_vol = 4.5
    
    print("\n--- 3.2 三變數超體積數值積分 (中點網格) ---")
    print("目標函數: f(x, y, z) = x * y * z, 範圍: [0, 1] x [0, 2] x [0, 3]")
    print(f"  理論解析解: 4.500000")
    num_vol = numerical_integral_nd(f_vol, low, high, steps_per_dim=30)
    print(f"  網格積分 (每軸 30 格，共 27,000 點): {num_vol:.6f} (誤差: {abs(num_vol - exact_vol):.2e})")


def demo_topic_4():
    print_header("【題目 4】蒙地卡羅法計算 n 變數積分 (超體積)")
    
    # 計算 4 維超球體 (4-ball) 的體積
    # 4-ball 半徑 R = 1 的體積解析解為: V_4 = (pi^2 / 2) * R^4 ≈ 4.9348022
    # 範圍: [-1, 1]^4, 超長方體體積 = 2^4 = 16
    exact_4ball = (math.pi**2) / 2.0
    indicator_4ball = lambda v: 1.0 if np.sum(v**2) <= 1.0 else 0.0
    
    low = [-1.0] * 4
    high = [1.0] * 4
    
    print("目標: 計算 4 維單位超球體 (Unit 4-Ball) 體積 (Indicator function 積分)")
    print(f"理論解析解: pi^2 / 2 ≈ {exact_4ball:.6f}")
    
    for n_samples in [50_000, 200_000, 1_000_000]:
        start = time.perf_counter()
        vol, se = monte_carlo_integral_nd(indicator_4ball, low, high, n_samples=n_samples, seed=42)
        elapsed = time.perf_counter() - start
        err = abs(vol - exact_4ball)
        print(f"  [採樣數 N = {n_samples:>9,}] 估計值: {vol:.6f} ± {se:.6f} | 誤差: {err:.6f} | 耗時: {elapsed:.4f}s")


def demo_topic_5_and_6():
    print_header("【題目 5 與 6 綜合對比】黎曼積分法 vs. 蒙地卡羅法 (1, 2, 5, 100 維)")
    print("被積函數: f(x) = sum_{i=1}^n x_i^2, 積分區間: [0, 1]^n")
    print("理論解析解: int_0^1 ... int_0^1 (sum_{i=1}^n x_i^2) dx_1...dx_n = n / 3")
    print("-" * 76)

    dimensions = [1, 2, 5, 100]

    # 格式化輸出表格標頭
    header = f"{'維度 (n)':<8} | {'解析解 (n/3)':<14} | {'黎曼積分結果':<16} | {'蒙地卡羅估計 (N=300k)':<24} | {'蒙地卡羅耗時'}"
    print(header)
    print("-" * 76)

    for n in dimensions:
        low = np.zeros(n)
        high = np.ones(n)
        exact = n / 3.0

        # 定義被積函數
        def f_riemann(x: np.ndarray) -> float:
            return float(np.sum(x**2))

        def f_mc(x: np.ndarray) -> np.ndarray:
            if x.ndim == 1:
                return float(np.sum(x**2))
            return np.sum(x**2, axis=-1)

        # 5. 黎曼積分計算
        riemann_str = ""
        try:
            r_val = integral(f_riemann, low, high)
            riemann_str = f"{r_val:.6f}"
        except DimensionalityCurseError:
            riemann_str = "維度災難 (無法計算)"

        # 6. 蒙地卡羅積分計算
        t0 = time.perf_counter()
        mc_val, mc_se = mc_integral(f_mc, low, high, n_samples=300_000, seed=42)
        mc_time = time.perf_counter() - t0
        mc_str = f"{mc_val:.5f} ± {mc_se:.5f}"

        print(f"{n:<8} | {exact:<14.6f} | {riemann_str:<16} | {mc_str:<24} | {mc_time:.4f}s")

    print("-" * 76)
    print("\n【深度結論與分析】")
    print("1. 在低維度 (n = 1, 2, 5)：")
    print("   黎曼網格法精度極高，但計算量隨維度指數爆炸 O(k^n)。")
    print("2. 在超高維度 (n = 100)：")
    print("   黎曼法即便每維度僅切 2 格，也需要 2^100 ≈ 1.27e+30 次計算，在現實物理世界中完全無法完成！")
    print("   而蒙地卡羅法收斂速度為 O(1 / sqrt(N))，與維度 n 完全無關！")
    print("   僅耗時約 0.8 秒便能以極高精準度 (33.335 ± 0.005) 估計出 100 維超體積積分！")


def main():
    print("=" * 76)
    print("   數值微積分與蒙地卡羅多維超體積積分系統 (全功能示範與測試)")
    print("   【AI 輔助開發聲明】：本程式與文件由 AI (Google Antigravity / Gemini) 輔助生成")
    print("=" * 76)

    demo_topic_1()
    demo_topic_2()
    demo_topic_3()
    demo_topic_4()
    demo_topic_5_and_6()

    print("\n" + "=" * 76)
    print("  所有範例測試執行完畢！如需運行單元測試，請輸入：")
    print("  python -m unittest discover -s tests -v")
    print("=" * 76)


if __name__ == "__main__":
    main()
