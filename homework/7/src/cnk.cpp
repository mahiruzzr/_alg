// C(n, k) = 從 n 個相異物中取出 k 個的組合數
//
//   動態規劃版：
//     1) top-down 記憶化（recursion + memo table）
//     2) bottom-up 逐步建表（Pascal 公式，1-D 滾動陣列）
//     3) bottom-up + 大整數（避免 64-bit 溢位）
//   非動態規劃版：
//     4) 連乘閉式解 C(n,k) = prod_{i=1..k} (n-k+i)/i（不遞迴、不建表）
//     5) double 浮點直算（示範精度陷阱，對應參考教材的 JS 例子）
//
// 用法：
//   cnk.exe                 完整展示
//   cnk.exe bench           各方法計時比較
//   cnk.exe big <n> <k>     大數驗證（DP vs 閉式解）

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

#include "bigint.h"

using Clock = std::chrono::steady_clock;

static double msSince(Clock::time_point t0) {
    return std::chrono::duration<double, std::milli>(Clock::now() - t0).count();
}

// ---------------------------------------------------------------------------
// 1) 純遞迴（沒有 DP，就是暴力展開）
//    C(n,k) = C(n-1,k-1) + C(n-1,k)
// ---------------------------------------------------------------------------
static unsigned long long g_calls = 0;

static unsigned long long cnkNaivePascal(int n, int k) {
    ++g_calls;
    if (k < 0 || k > n) return 0;
    if (k == 0 || n <= 1) return 1;
    return cnkNaivePascal(n - 1, k) + cnkNaivePascal(n - 1, k - 1);
}

// ---------------------------------------------------------------------------
// 2) 動態規劃：top-down 記憶化（查表法）
// ---------------------------------------------------------------------------
static unsigned long long cnkMemo(int n, int k, std::vector<std::vector<unsigned long long>>& memo,
                                  unsigned long long& calls) {
    if (k < 0 || k > n) return 0;
    if (k == 0 || n <= 1) return 1;
    if (memo[n][k] != 0) return memo[n][k];
    ++calls;
    memo[n][k] = cnkMemo(n - 1, k, memo, calls) + cnkMemo(n - 1, k - 1, memo, calls);
    return memo[n][k];
}

// ---------------------------------------------------------------------------
// 3) 動態規劃：bottom-up 逐步建表（Pascal 公式），1-D 陣列
// ---------------------------------------------------------------------------
static unsigned long long cnkBottomUp(int n, int k) {
    if (k < 0 || k > n) return 0;
    k = std::min(k, n - k);
    std::vector<unsigned long long> dp(k + 1, 0);
    dp[0] = 1;
    for (int i = 1; i <= n; ++i) {
        for (int j = std::min(i, k); j >= 1; --j) {
            dp[j] += dp[j - 1];
        }
    }
    return dp[k];
}

// ---------------------------------------------------------------------------
// 4) 非動態規劃：連乘閉式解（純公式，不遞迴、不建表）
// ---------------------------------------------------------------------------
static BigUInt cnkClosedFormBig(int n, int k) {
    if (k < 0 || k > n) return BigUInt(0);
    k = std::min(k, n - k);
    BigUInt r(1);
    for (int i = 1; i <= k; ++i) {
        r *= BigUInt(static_cast<uint64_t>(n - k + i));
        uint32_t rem = 0;
        r = r.divSmall(static_cast<uint32_t>(i), &rem);
        if (rem != 0) {
            std::fprintf(stderr, "internal error: division not exact at i=%d\n", i);
        }
    }
    return r;
}

// ---------------------------------------------------------------------------
// 5) 動態規劃 + 大數：bottom-up 建表，用 BigUInt 避免溢位
// ---------------------------------------------------------------------------
static BigUInt cnkBottomUpBig(int n, int k) {
    if (k < 0 || k > n) return BigUInt(0);
    k = std::min(k, n - k);
    std::vector<BigUInt> dp(k + 1);
    dp[0] = BigUInt(1);
    for (int i = 1; i <= n; ++i) {
        for (int j = std::min(i, k); j >= 1; --j) {
            dp[j] += dp[j - 1];
        }
    }
    return dp[k];
}

// ---------------------------------------------------------------------------
// 6) 浮點直算：示範「不建表也可能算錯」
// ---------------------------------------------------------------------------
static double factorialDouble(int n) {
    double p = 1;
    for (int i = 1; i <= n; ++i) p *= i;
    return p;
}

static double cnkDouble(int n, int k) {
    return factorialDouble(n) / (factorialDouble(k) * factorialDouble(n - k));
}

// ---------------------------------------------------------------------------

static void showBasics() {
    std::printf("== 1. Naive recursion (non-DP) ==\n");
    for (int n : {10, 20, 25, 28, 30}) {
        g_calls = 0;
        auto t0 = Clock::now();
        unsigned long long v = cnkNaivePascal(n, n / 2);
        double ms = msSince(t0);
        std::printf("   C(%2d,%2d) = %-20llu calls = %-12llu %10.3f ms\n", n, n / 2, v, g_calls, ms);
    }
    std::printf("   -> calls ~double each step: exponential O(2^n)\n");
    std::printf("      C(60,30) would need about 3e17 calls\n\n");

    std::printf("== 2. DP: top-down memoization ==\n");
    for (int n : {30, 60, 75, 90, 120}) {
        std::vector<std::vector<unsigned long long>> memo(n + 1, std::vector<unsigned long long>(n + 1, 0));
        unsigned long long calls = 0;
        auto t0 = Clock::now();
        unsigned long long v = cnkMemo(n, n / 2, memo, calls);
        double ms = msSince(t0);
        const std::string exact = cnkBottomUpBig(n, n / 2).str();
        const bool fits = (exact == std::to_string(v));
        std::printf("   C(%3d,%3d) = %-20llu calls = %-8llu %8.3f ms  %s\n", n, n / 2, v, calls, ms,
                    fits ? "exact" : "OVERFLOW");
    }
    std::printf("   -> each (n,k) computed once: O(n*k) work, O(n*k) space\n\n");

    std::printf("== 3. DP: bottom-up tabulation (1-D array) ==\n");
    for (int n : {60, 90, 120, 300, 1000}) {
        auto t0 = Clock::now();
        unsigned long long v = cnkBottomUp(n, n / 2);
        double ms = msSince(t0);
        const std::string exact = cnkBottomUpBig(n, n / 2).str();
        const bool fits = (exact == std::to_string(v));
        std::printf("   C(%4d,%4d) = %-20llu %8.3f ms  (time O(n*k), space O(k))  %s\n", n, n / 2, v, ms,
                    fits ? "exact" : "OVERFLOW -> needs BigUInt");
    }
    std::printf("\n");

    std::printf("== 4. Non-DP: closed-form product ==\n");
    for (int n : {60, 120, 300, 1000}) {
        auto t0 = Clock::now();
        BigUInt v = cnkClosedFormBig(n, n / 2);
        double ms = msSince(t0);
        std::printf("   C(%4d,%4d) = %-40s %10.3f ms  (O(k) mul/div)\n", n, n / 2, v.str().c_str(), ms);
    }
    std::printf("\n");

    std::printf("== 5. Precision trap: plain double ==\n");
    for (int n : {20, 40, 60}) {
        double d = cnkDouble(n, n / 2);
        BigUInt exact = cnkClosedFormBig(n, n / 2);
        std::printf("   n=%2d  double = %-22.0f exact = %-22s\n", n, d, exact.str().c_str());
    }
    std::printf("   -> double has 53 significant bits; C(60,30) exact = 118264581564861424\n");
    std::printf("      double gives 118264581564861472 (JS gives ...470): both wrong\n");
    std::printf("      => use DP + big integers, not the raw factorial formula\n\n");

    std::printf("== 6. DP + big integers (bottom-up, BigUInt) ==\n");
    for (int n : {60, 200, 1000}) {
        auto t0 = Clock::now();
        BigUInt v = cnkBottomUpBig(n, n / 2);
        double ms = msSince(t0);
        std::string s = v.str();
        std::printf("   C(%4d,%4d) = %-60s %10.3f ms  (digits=%zu)\n", n, n / 2, s.c_str(), ms, s.size());
    }
    std::printf("\n");
}

static void bench() {
    std::printf("%-6s %-13s %-12s %-13s %-13s %-12s\n", "n", "naive(rec)", "memo(DP)", "bottomup(DP)",
                "closedform", "BigUIntDP");
    for (int n : {18, 22, 26, 30, 32}) {
        g_calls = 0;
        auto t0 = Clock::now();
        cnkNaivePascal(n, n / 2);
        double tNaive = msSince(t0);
        unsigned long long callsNaive = g_calls;

        std::vector<std::vector<unsigned long long>> memo(n + 1, std::vector<unsigned long long>(n + 1, 0));
        unsigned long long calls = 0;
        t0 = Clock::now();
        cnkMemo(n, n / 2, memo, calls);
        double tMemo = msSince(t0);

        t0 = Clock::now();
        cnkBottomUp(n, n / 2);
        double tBU = msSince(t0);

        t0 = Clock::now();
        cnkClosedFormBig(n, n / 2);
        double tCF = msSince(t0);

        t0 = Clock::now();
        cnkBottomUpBig(n, n / 2);
        double tBig = msSince(t0);

        std::printf("%-6d %8.3f ms   %8.3f ms  %8.3f ms    %8.3f ms   %8.3f ms   (naive calls=%llu)\n", n, tNaive,
                    tMemo, tBU, tCF, tBig, callsNaive);
    }
}

static void bigCheck(int n, int k) {
    BigUInt a = cnkBottomUpBig(n, k);
    BigUInt b = cnkClosedFormBig(n, k);
    std::printf("C(%d,%d)\n  DP (bottom-up + BigUInt) : %s\n  closed-form               : %s\n  match = %s\n", n, k,
                a.str().c_str(), b.str().c_str(), a.str() == b.str() ? "YES" : "NO");
}

int main(int argc, char** argv) {
    std::string cmd = argc > 1 ? argv[1] : "show";
    if (cmd == "show") {
        showBasics();
    } else if (cmd == "bench") {
        bench();
    } else if (cmd == "big") {
        int n = argc > 2 ? std::atoi(argv[2]) : 200;
        int k = argc > 3 ? std::atoi(argv[3]) : 100;
        bigCheck(n, k);
    } else {
        std::printf("usage: cnk [show|bench|big n k]\n");
        return 1;
    }
    return 0;
}
