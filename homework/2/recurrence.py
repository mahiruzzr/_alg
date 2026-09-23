# 四題遞迴方程式：遞迴實作 + 封閉解驗證 + 複雜度展示
import math
import time


# 1. T(n) = T(n-1) + 8, T(1) = 1  ->  8n - 7, O(n)
def T1_rec(n):
    if n == 1:
        return 1
    return T1_rec(n - 1) + 8


def T1_closed(n):
    return 8 * n - 7


# 2. T(n) = 2*T(n-1) + 9, T(1) = 1  ->  5*2^n - 9, O(2^n)
def T2_rec(n):
    if n == 1:
        return 1
    return 2 * T2_rec(n - 1) + 9


def T2_closed(n):
    return 5 * (2 ** n) - 9


# 3. T(n) = 2*T(n/2) + 1, T(1) = 1  ->  2n - 1 (n 為 2 的冪), O(n)
def T3_rec(n):
    if n == 1:
        return 1
    return 2 * T3_rec(n // 2) + 1


def T3_closed(n):
    return 2 * n - 1


# 4. T(n) = T(n/2) + 1, T(1) = 1  ->  log2(n) + 1 (n 為 2 的冪), O(log n)
def T4_rec(n):
    if n == 1:
        return 1
    return T4_rec(n // 2) + 1


def T4_closed(n):
    return int(math.log2(n)) + 1


def check(name, rec, closed, ns):
    print(f"{name}:")
    for n in ns:
        r = rec(n)
        c = closed(n)
        ok = "OK" if r == c else f"FAIL (rec={r}, closed={c})"
        print(f"  n={n:<5} rec={r:<12} closed={c:<12} {ok}")


if __name__ == "__main__":
    # 正確性驗證
    check("T1(n)=T(n-1)+8", T1_rec, T1_closed, [1, 2, 5, 10, 100])
    check("T2(n)=2T(n-1)+9", T2_rec, T2_closed, [1, 2, 5, 10, 20])
    # T3/T4 只在 2 的冪上有精確封閉解
    check("T3(n)=2T(n/2)+1", T3_rec, T3_closed, [1, 2, 4, 8, 16, 64, 1024])
    check("T4(n)=T(n/2)+1", T4_rec, T4_closed, [1, 2, 4, 8, 16, 64, 1024])

    # 成長速度展示：同一個 n 下數值差異
    print("\n成長速度比較 (封閉解):")
    print(f"{'n':<8}{'T1=8n-7':<14}{'T2=5*2^n-9':<16}{'T3=2n-1':<12}{'T4=log2n+1'}")
    for n in [4, 8, 16, 20]:
        print(f"{n:<8}{T1_closed(n):<14}{T2_closed(n):<16}{T3_closed(n):<12}{T4_closed(n)}")

    # 執行時間展示：T2 是指數級，n 稍大就明顯變慢
    print("\n執行時間比較 (遞迴版):")
    for name, fn, n in [("T1", T1_rec, 500), ("T2", T2_rec, 20),
                        ("T3", T3_rec, 1024), ("T4", T4_rec, 1024)]:
        t0 = time.perf_counter()
        fn(n)
        dt = (time.perf_counter() - t0) * 1000
        print(f"  {name}(n={n}): {dt:.3f} ms")
