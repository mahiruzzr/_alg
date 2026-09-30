# 自訂問題:用迭代法求 cbrt(2) (即解 x^3 = 2)
# 對照教材 iterative3.py (求 sqrt(3) 的三種迭代式),本程式設計三種解同一方程的不動點迭代:
#   真值 alpha = 2^(1/3) 約 1.25992104989
#
# 原理:把 f(x)=x^3-2=0 改寫成 x = g(x),再迭代 x_{n+1} = g(x_n)
# 收斂直觀條件:若在不動點附近 |g'(alpha)| < 1 則(局部)收斂,越小越快;
# 若 |g'(alpha)| > 1 則發散;若 g'(alpha)=0 則通常二階以上快速收斂(牛頓法)。

g1 = lambda x: 2 / (x * x)              # 由 x^3=2 直接得 x=2/x^2 (對應教材 f1=3/x)
g2 = lambda x: x - 0.1 * (x**3 - 2)     # 阻尼/梯度式:x - k*f(x),k=0.1 (對應教材 f2)
g3 = lambda x: (2*x + 2/(x*x)) / 3      # 牛頓法:x - f/f' = x-(x^3-2)/(3x^2) (對應教材 f3)

# 導數分析(用於預測收斂性):
# g1'(x) = -4/x^3, 在 alpha 處 = -4/2 = -2, |g1'|=2 > 1, 發散
# g2'(x) = 1-0.3*x^2, 在 alpha 處 = 1-0.3*2^(2/3) 約 0.524 < 1, 線性收斂
# g3'(x) 在 alpha 處 = 0, 二階收斂(最快)

def run(g, x0, steps):
    """獨立執行一種迭代,遇到溢位/除零就停下並標記發散。回傳歷史串列。"""
    hist = []
    x = x0
    for _ in range(steps):
        try:
            x = g(x)
            if abs(x) > 1e15 or x != x:  # inf 或 nan 視為發散
                hist.append(float('inf'))
                break
            hist.append(x)
        except ZeroDivisionError:
            hist.append(float('inf'))
            break
    return hist

if __name__ == "__main__":
    alpha = 2 ** (1/3)
    print(f"真值 cbrt(2) = {alpha:.10f}")
    print(" i | g1:2/x^2(發散) | g2:阻尼(線性) | g3:牛頓(二階)")
    print("-" * 60)

    h1 = run(g1, 1.0, 20)
    h2 = run(g2, 1.0, 20)
    h3 = run(g3, 1.0, 20)

    def fmt(v):
        if v == float('inf'):
            return "發散/溢位"
        return f"{v:14.10f}"

    for i in range(20):
        s1 = fmt(h1[i]) if i < len(h1) else "發散/溢位"
        s2 = fmt(h2[i]) if i < len(h2) else "發散/溢位"
        s3 = fmt(h3[i]) if i < len(h3) else "發散/溢位"
        print(f"{i+1:2d} | {s1} | {s2} | {s3}")
        if s1.startswith("發散") and i >= 7:
            # g1 早已發散,後面不再有意義,但繼續印出 g2/g3 以便對比
            pass

    print("\n--- 結論 ---")
    print(f"g1: 初值1 -> 2 -> 0.5 -> 8 -> 0.03 -> 2048 -> ... 迅速溢位, 發散(比教材 f1 的 1<->3 震盪更劇烈)。")
    print(f"    原因 |g1'(alpha)|=2>1, 誤差每步放大約 2 倍。")
    print(f"g2 最終 x={h2[-1]:.10f}, 誤差={abs(h2[-1]-alpha):.2e}, 線性收斂, 約每步誤差剩 0.5 倍, 20 步達 1e-4。")
    print(f"g3 最終 x={h3[-1]:.10f}, 誤差={abs(h3[-1]-alpha):.2e}, 5 步內達 double 精度, 二階收斂。")
    print("心得:同一方程改寫成不同 g(x),收斂性天差地別。設計迭代式的關鍵就是讓 |g'(alpha)| 盡量小。")
