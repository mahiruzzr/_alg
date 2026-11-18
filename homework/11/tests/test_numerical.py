"""
單元測試套件 (Unit Tests for Numerical Methods & Monte Carlo)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本測試程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計與撰寫。
This test suite was designed and implemented with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================
"""

import unittest
import math
import numpy as np

import sys
from pathlib import Path
# 將專案根目錄加入模組搜尋路徑
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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


class TestNumericalMethods(unittest.TestCase):
    """測試 1-6 題所有演算法之正確性與數值精準度"""

    # -------------------------------------------------------------------------
    # 題目 1: 單變數數值微分與積分測試
    # -------------------------------------------------------------------------
    def test_single_variable_differentiation(self):
        """測試單變數數值微分 (中心差分、前向差分、後向差分)"""
        # f(x) = x^3 - 2x + 4, f'(x) = 3x^2 - 2
        f = lambda x: x**3 - 2.0 * x + 4.0
        x0 = 3.0
        exact_deriv = 3.0 * (x0**2) - 2.0  # 25.0

        deriv_central = numerical_diff_1d(f, x0, h=1e-5, method="central")
        deriv_forward = numerical_diff_1d(f, x0, h=1e-5, method="forward")
        deriv_backward = numerical_diff_1d(f, x0, h=1e-5, method="backward")

        self.assertAlmostEqual(deriv_central, exact_deriv, places=5)
        self.assertAlmostEqual(deriv_forward, exact_deriv, places=3)
        self.assertAlmostEqual(deriv_backward, exact_deriv, places=3)

    def test_single_variable_integration(self):
        """測試單變數數值積分 (辛普森法、梯形法、中點法)"""
        # f(x) = sin(x), int_0^pi sin(x) dx = -cos(pi) - (-cos(0)) = 2.0
        f = math.sin
        exact_integral = 2.0

        val_simpson = numerical_integral_1d(f, 0.0, math.pi, n_steps=200, method="simpson")
        val_trapezoid = numerical_integral_1d(f, 0.0, math.pi, n_steps=1000, method="trapezoid")
        val_midpoint = numerical_integral_1d(f, 0.0, math.pi, n_steps=1000, method="midpoint")

        self.assertAlmostEqual(val_simpson, exact_integral, places=5)
        self.assertAlmostEqual(val_trapezoid, exact_integral, places=4)
        self.assertAlmostEqual(val_midpoint, exact_integral, places=4)

    # -------------------------------------------------------------------------
    # 題目 2: 單變數蒙地卡羅積分測試
    # -------------------------------------------------------------------------
    def test_single_variable_monte_carlo(self):
        """測試單變數蒙地卡羅積分"""
        # f(x) = x^2, int_0^1 x^2 dx = 1/3
        f = lambda x: x**2
        exact_val = 1.0 / 3.0

        val, se = monte_carlo_integral_1d(f, 0.0, 1.0, n_samples=150_000, seed=12345)
        # 驗證誤差落在 3 倍標準誤之內 (機率約 99.7%)
        self.assertLessEqual(abs(val - exact_val), 3.0 * se)

    # -------------------------------------------------------------------------
    # 題目 3: 多變數微分 (梯度) 與超體積數值積分測試
    # -------------------------------------------------------------------------
    def test_multivariable_gradient(self):
        """測試 n 變數數值梯度"""
        # f(x, y, z) = x^2 + 2*y^2 - 3*z^2
        # grad f = [2x, 4y, -6z]
        # 在 (2, -1, 3) 處: [4, -4, -18]
        f = lambda v: v[0]**2 + 2.0 * v[1]**2 - 3.0 * v[2]**2
        pt = [2.0, -1.0, 3.0]
        grad_exact = np.array([4.0, -4.0, -18.0])

        grad_num = numerical_gradient(f, pt, h=1e-6)
        np.testing.assert_allclose(grad_num, grad_exact, rtol=1e-5, atol=1e-5)

    def test_multivariable_hypervolume_integral(self):
        """測試 n 變數超體積數值積分 (中點網格)"""
        # f(x, y) = x * y, [0, 1] x [0, 2]
        # int_0^1 x dx * int_0^2 y dy = 0.5 * 2 = 1.0
        f = lambda v: v[0] * v[1]
        val = numerical_integral_nd(f, low=[0.0, 0.0], high=[1.0, 2.0], steps_per_dim=50)
        self.assertAlmostEqual(val, 1.0, places=4)

    # -------------------------------------------------------------------------
    # 題目 4: 多變數蒙地卡羅超體積積分測試
    # -------------------------------------------------------------------------
    def test_multivariable_monte_carlo(self):
        """測試 n 變數蒙地卡羅超體積積分"""
        # f(x, y, z) = 1 (常數函數，積分即為長方體體積)
        # [0, 2] x [0, 3] x [0, 4] -> 體積 = 2 * 3 * 4 = 24.0
        f = lambda v: 1.0
        val, se = monte_carlo_integral_nd(f, low=[0, 0, 0], high=[2, 3, 4], n_samples=20_000, seed=42)
        self.assertAlmostEqual(val, 24.0, places=4)

    # -------------------------------------------------------------------------
    # 題目 5: 黎曼積分法 integral(f, low, high) (1D, 2D, 5D, 100D)
    # -------------------------------------------------------------------------
    def test_question_5_riemann_integral(self):
        """測試第 5 題：黎曼積分 integral(f, low, high) 在 1, 2, 5 維的正確性"""
        f = lambda x: float(np.sum(x**2))

        # 1 維: 1/3 ≈ 0.333333
        val_1d = integral(f, [0.0], [1.0])
        self.assertAlmostEqual(val_1d, 1.0 / 3.0, places=4)

        # 2 維: 2/3 ≈ 0.666667
        val_2d = integral(f, [0.0, 0.0], [1.0, 1.0])
        self.assertAlmostEqual(val_2d, 2.0 / 3.0, places=3)

        # 5 維: 5/3 ≈ 1.666667
        val_5d = integral(f, [0.0]*5, [1.0]*5)
        self.assertAlmostEqual(val_5d, 5.0 / 3.0, places=1)

    def test_question_5_dimensionality_curse(self):
        """測試第 5 題：100 維時正確觸發維度災難例外 (DimensionalityCurseError)"""
        f = lambda x: float(np.sum(x**2))
        low = np.zeros(100)
        high = np.ones(100)

        with self.assertRaises(DimensionalityCurseError) as context:
            integral(f, low, high)

        self.assertIn("維度災難", str(context.exception))
        self.assertIn("100", str(context.exception))

    # -------------------------------------------------------------------------
    # 題目 6: 蒙地卡羅法 mc_integral(f, low, high) (1D, 2D, 5D, 100D)
    # -------------------------------------------------------------------------
    def test_question_6_mc_integral(self):
        """測試第 6 題：蒙地卡羅法在 1, 2, 5, 100 維的表現"""
        def f(x: np.ndarray) -> np.ndarray:
            if x.ndim == 1:
                return float(np.sum(x**2))
            return np.sum(x**2, axis=-1)

        test_cases = [
            (1, 1.0 / 3.0),
            (2, 2.0 / 3.0),
            (5, 5.0 / 3.0),
            (100, 100.0 / 3.0),
        ]

        for n, exact_val in test_cases:
            low = np.zeros(n)
            high = np.ones(n)
            val, se = mc_integral(f, low, high, n_samples=250_000, seed=42)

            # 統計檢驗: 數值誤差應在 3 倍標準誤之內
            error = abs(val - exact_val)
            self.assertLessEqual(
                error, 3.5 * se,
                f"維度 n={n} 蒙地卡羅誤差 {error} 超過允許容許範圍 (3.5 * SE = {3.5 * se})"
            )


if __name__ == "__main__":
    unittest.main()
