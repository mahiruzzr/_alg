"""
數值微積分與蒙地卡羅方法工具包 (Numerical Calculus & Monte Carlo Package)

=============================================================================
【AI 使用聲明 / AI Usage Declaration】
本程式碼完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫與最佳化。
This code was designed, implemented, and optimized with the assistance of AI
(Google Antigravity / Gemini).
=============================================================================
"""

from .single_variable import (
    numerical_diff_1d,
    numerical_integral_1d,
    monte_carlo_integral_1d,
)
from .multivariable import (
    numerical_gradient,
    numerical_integral_nd,
    monte_carlo_integral_nd,
)
from .riemann import (
    integral,
    DimensionalityCurseError,
)
from .mc_integral import (
    mc_integral,
)

__all__ = [
    "numerical_diff_1d",
    "numerical_integral_1d",
    "monte_carlo_integral_1d",
    "numerical_gradient",
    "numerical_integral_nd",
    "monte_carlo_integral_nd",
    "integral",
    "DimensionalityCurseError",
    "mc_integral",
]
