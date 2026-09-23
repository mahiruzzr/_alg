# 方法 1：直接次方
def power2n_v1(n):
    return 2**n


# 方法 2a：用遞迴 power2n(n-1)+power2n(n-1)
# 時間複雜度 O(2^n)，n=100 跑不出來
def power2n_v2a(n):
    if n == 0:
        return 1
    return power2n_v2a(n-1) + power2n_v2a(n-1)


# 方法 2b：用遞迴 2*power2n(n-1)
# 時間複雜度 O(n)
def power2n_v2b(n):
    if n == 0:
        return 1
    return 2 * power2n_v2b(n-1)


# 方法 3：用遞迴+查表 (memoization)
# 時間複雜度 O(n)，但避免重複計算，概念上和 2a 一樣只是加了記憶
_memo = {0: 1}
def power2n_v3(n, memo=None):
    if memo is None:
        memo = _memo
    if n in memo:
        return memo[n]
    if n == 0:
        return 1
    # 只算一次 power2n(n-1)，存起來用兩次
    half = power2n_v3(n-1, memo)
    memo[n] = half + half
    return memo[n]


if __name__ == "__main__":
    import time

    N = 100
    expected = 2**100
    print(f"2^100 = {expected}\n")

    # --- 方法1 ---
    t0 = time.perf_counter()
    r1 = power2n_v1(N)
    t1 = time.perf_counter()
    print(f"方法1 (2**n)          : {r1 == expected}, 耗時 {(t1-t0)*1e6:.2f} us")

    # --- 方法2b ---
    t0 = time.perf_counter()
    r2b = power2n_v2b(N)
    t1 = time.perf_counter()
    print(f"方法2b (2*rec(n-1))   : {r2b == expected}, 耗時 {(t1-t0)*1e6:.2f} us")

    # --- 方法3 ---
    _memo.clear()
    _memo[0] = 1
    t0 = time.perf_counter()
    r3 = power2n_v3(N)
    t1 = time.perf_counter()
    print(f"方法3 (遞迴+查表)      : {r3 == expected}, 耗時 {(t1-t0)*1e6:.2f} us")

    # --- 方法2a：n=100 跑不出來，這裡用小 n 示範指數爆炸 ---
    print("\n方法2a (rec(n-1)+rec(n-1)) 在 n=100 呼叫次數約 2^101，跑不出來。改用小 n 示範：")
    for n_small in [10, 15, 20, 22]:
        t0 = time.perf_counter()
        r2a = power2n_v2a(n_small)
        t1 = time.perf_counter()
        print(f"  n={n_small:<3} 結果正確={r2a == 2**n_small}, 耗時 {(t1-t0)*1000:.3f} ms")
    print("  n=100 預估耗時: 2^(100-22) * 上面 n=22 的時間 = 天文數字，出不來。")
