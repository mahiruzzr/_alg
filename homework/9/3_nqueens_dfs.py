"""問題 3：八皇后 (DFS + 剪枝 = 回溯法)

一列放一個皇后：queens[r] = c（第 r 列的皇后放在第 c 行）。
逐列往下搜，放不下就退回上一列換個位置。
"""


def attacked(queens, row, col):
    """(row, col) 是否被前面 row 列的任一個皇后攻擊？"""
    for i in range(row):
        if queens[i] == col:                      # 同一行
            return True
        if abs(queens[i] - col) == row - i:       # 兩種對角線
            return True
    return False


def solve(n=8, prune=True):
    """回傳 (所有解, 展開的節點數)。

    prune=True ：DFS + 剪枝，放下去會被打的格子直接不遞迴
    prune=False：純 DFS，n^n 種放法全部走到底再檢查（對照用）
    """
    solutions, queens, nodes = [], [], 0

    def dfs(row):
        nonlocal nodes
        nodes += 1
        if row == n:
            if prune or all(not attacked(queens, r, queens[r]) for r in range(n)):
                solutions.append(queens.copy())
            return
        for col in range(n):
            if prune and attacked(queens, row, col):
                continue                          # 剪枝！
            queens.append(col)
            dfs(row + 1)
            queens.pop()                          # 回溯

    dfs(0)
    return solutions, nodes


def show(sol):
    n = len(sol)
    for r in range(n):
        print(" ".join("Q" if sol[r] == c else "." for c in range(n)))


if __name__ == "__main__":
    sols, nodes = solve(8, prune=True)
    print(f"共找到 {len(sols)} 組解（理論值 92），剪枝版展開 {nodes:,} 個節點")
    print(f"（不剪枝要展開 (8^9-1)/7 = {(8**9 - 1)//7:,} 個節點）")
    print(f"\n解 1：行號序列 = {sols[0]}")
    show(sols[0])

    # 同樣問題在 n=6 實測「不剪枝」與「剪枝」的差距
    s_p, n_p = solve(6, prune=True)
    s_b, n_b = solve(6, prune=False)
    print(f"\n對照 N=6：剪枝 {n_p:,} 節點、不剪枝 {n_b:,} 節點，解數皆為 {len(s_p)} = {len(s_b)}")

    print("\n不同 N 的解數：")
    for n in range(4, 11):
        print(f"  N={n:>2} → {len(solve(n)[0]):>4} 組解")
