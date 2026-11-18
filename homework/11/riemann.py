"""
第 5 題：黎曼積分法多變數積分模組 (Riemann Hypervolume Integration)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫與最佳化。
This code was designed, implemented, and optimized with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================

題目需求：
5. 請用黎曼積分法，寫函數 integral(f, low, high) 來做 n 變數積分（n 是 low, high 的陣列長度）
    * 請分別用 1 維, 2 維, 5 維, 100 維來計算
    * 範例用 f(x) = x_1^2 + ... + x_n^2 , low=0, high=1
"""

from typing import Callable, Sequence, Union, Optional
import itertools
import numpy as np


class DimensionalityCurseError(OverflowError):
    """當維度過高導致黎曼網格評估點數爆炸（維度災難）時拋出的自訂例外。"""
    pass


def integral(
    f: Callable[[np.ndarray], float],
    low: Union[Sequence[float], np.ndarray],
    high: Union[Sequence[float], np.ndarray],
    steps_per_dim: Optional[int] = None,
    max_evaluations: int = 2_000_000
) -> float:
    """
    使用黎曼中點網格法 (Riemann Midpoint Sum) 計算 n 變數超體積積分。

    數學定義:
        I = int_{low_1}^{high_1} ... int_{low_n}^{high_n} f(x_1, ..., x_n) dx_1 ... dx_n
        ≈ sum_{i_1} ... sum_{i_n} f(m_{i_1}, ..., m_{i_n}) * dV
        其中 dV = prod_{d=1}^n ((high_d - low_d) / steps_d)

    參數:
        f: 被積函數 f(x)，接受長度為 n 的一維 numpy 陣列或序列，回傳純量 float
        low: 各維度積分下限陣列，例如 [0, 0, ...]
        high: 各維度積分上限陣列，例如 [1, 1, ...]
        steps_per_dim: 每個維度切分的步數 k。若為 None，則自動根據維度 n 選擇安全步數:
                       - 1 維: 1000 步
                       - 2 維: 100 步 (共 10,000 點)
                       - 5 維: 10 步 (共 100,000 點)
                       - n 維: 若 k^n > max_evaluations 則引發維度災難警告
        max_evaluations: 允許的最大評估點數 (預設 2,000,000 點)

    回傳:
        黎曼積分估計值 (float)

    例外:
        ValueError: 當 low 與 high 長度不一致，或上限小於下限時
        DimensionalityCurseError: 當網格點數 steps_per_dim^n 超過計算極限時
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

    # 自適應選擇各維度切分步數 (若使用者未指定)
    if steps_per_dim is None:
        if n == 1:
            steps_per_dim = 1000
        elif n == 2:
            steps_per_dim = 100
        elif n <= 5:
            steps_per_dim = 10
        else:
            # 高維度下即便每軸僅切 2 格，總點數也高達 2^n
            steps_per_dim = 2

    # 計算總評估點數: steps_per_dim^n
    # 針對 n 很大時 (例如 n=100)，使用浮點數對數或直接計算以防止記憶體崩潰
    if n * np.log10(steps_per_dim) > np.log10(max_evaluations):
        approx_total = float(steps_per_dim) ** n
        raise DimensionalityCurseError(
            f"\n【維度災難 (Curse of Dimensionality)】\n"
            f"當維度 n = {n}，即便每維度僅切分 {steps_per_dim} 格，"
            f"黎曼網格所需的總取樣點數為 {steps_per_dim}^{n} ≈ {approx_total:.2e} 點！\n"
            f"若以每秒計算 10 億 (10^9) 次點評估計算，需要約 "
            f"{(approx_total / 1e9 / (365.25 * 86400)):.2e} 年才能完成。\n"
            f"因此傳統黎曼網格法在 100 維下無法於有限時間內完成。\n"
            f"這正是第 6 題改用蒙地卡羅法 (Monte Carlo) 的核心原因！"
        )

    # 計算各軸步長與中點
    dx = (high_arr - low_arr) / steps_per_dim
    dV = float(np.prod(dx))

    # 各維度中點
    dim_midpoints = [
        low_arr[d] + (np.arange(steps_per_dim) + 0.5) * dx[d]
        for d in range(n)
    ]

    # 累加黎曼中點和
    total_sum = 0.0
    for pt in itertools.product(*dim_midpoints):
        total_sum += f(np.array(pt))

    return float(total_sum * dV)


def run_riemann_benchmark():
    """
    執行第 5 題的要求：
    分別用 1 維, 2 維, 5 維, 100 維測試 f(x) = sum(x_i^2), low=0, high=1
    """
    import time

    print("=" * 70)
    print("第 5 題：黎曼積分法 integral(f, low, high) 基準測試")
    print("被積函數: f(x) = x_1^2 + x_2^2 + ... + x_n^2, 範圍: [0, 1]^n")
    print("理論解析解: int_0^1 ... int_0^1 (sum x_i^2) dx = n / 3")
    print("=" * 70)

    dimensions = [1, 2, 5, 100]

    for n in dimensions:
        low = np.zeros(n)
        high = np.ones(n)
        exact_value = n / 3.0

        # 定義被積函數 f(x) = sum(x_i^2)
        f = lambda x: float(np.sum(x**2))

        print(f"\n--- [維度 n = {n}] ---")
        print(f"理論解析解: {n}/3 = {exact_value:.6f}")

        start_time = time.perf_counter()
        try:
            val = integral(f, low, high)
            elapsed = time.perf_counter() - start_time
            error = abs(val - exact_value)
            print(f"黎曼積分結果: {val:.6f}")
            print(f"絕對誤差:     {error:.6e}")
            print(f"執行耗時:     {elapsed:.4f} 秒")
        except DimensionalityCurseError as e:
            elapsed = time.perf_counter() - start_time
            print(f"執行結果:     無法以傳統黎曼網格法計算 (觸發保護機制)")
            print(f"說明資訊:     {e}")
            print(f"耗時 (檢測):  {elapsed:.4f} 秒")


if __name__ == "__main__":
    run_riemann_benchmark()
