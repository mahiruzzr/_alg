// diff 兩種解法的對照工具
//   1) 動態規劃：LCS DP 表 + 回溯          -> diffLcsDp()
//   2) 非動態規劃：Myers O(ND) 貪婪 + 回溯  -> diffMyers()
//
// 用法：
//   diff_main demo                 內建範例
//   diff_main selftest              隨機對拍 + 邊界案例
//   diff_main bench [N] [D]        基準測試：N 行、相差 D 處
//   diff_main file <a.txt> <b.txt> [dp|myers]   對兩個檔案做 diff

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <vector>

#include "diff_dp.h"
#include "diff_myers.h"
#include "diff_types.h"

using Clock = std::chrono::steady_clock;

static double msSince(Clock::time_point t0) {
    return std::chrono::duration<double, std::milli>(Clock::now() - t0).count();
}

struct Stat {
    long long equal = 0, del = 0, ins = 0;
};

static Stat statOf(const std::vector<Op>& ops) {
    Stat s;
    for (const Op& o : ops) {
        if (o.kind == OpKind::Equal) ++s.equal;
        else if (o.kind == OpKind::Delete) ++s.del;
        else ++s.ins;
    }
    return s;
}

static const char* kSampleA = R"(int main() {
    int a = 1;
    int b = 2;
    printf("hello world\n");
    return 0;
}
)";

static const char* kSampleB = R"(int main() {
    int a = 1;
    int c = 2;
    printf("hello, world\n");
    return 0;
}
)";

static void demo() {
    std::vector<std::string> A = splitLines(kSampleA);
    std::vector<std::string> B = splitLines(kSampleB);

    auto t0 = Clock::now();
    std::vector<Op> dp = diffLcsDp(A, B);
    double dpMs = msSince(t0);

    t0 = Clock::now();
    std::vector<Op> my = diffMyers(A, B);
    double myMs = msSince(t0);

    std::printf("=== DP version: LCS table + backtrack ===\n");
    printDiff(A, B, dp);
    std::printf("\n=== Non-DP version: Myers O(ND) greedy ===\n");
    printDiff(A, B, my);

    Stat sd = statOf(dp), sm = statOf(my);
    std::printf("\nDP   : equal=%lld del=%lld ins=%lld  (%.3f ms)\n", sd.equal, sd.del, sd.ins, dpMs);
    std::printf("Myers: equal=%lld del=%lld ins=%lld  (%.3f ms)\n", sm.equal, sm.del, sm.ins, myMs);
}

// 產生兩份「相似度可控」的文件
static void makePair(int n, int edits, unsigned seed,
                     std::vector<std::string>& A, std::vector<std::string>& B) {
    std::mt19937 rng(seed);
    A.clear();
    B.clear();
    for (int i = 0; i < n; ++i) {
        std::string line = "func line_" + std::to_string(i) + " value_" + std::to_string(rng() % 100000);
        A.push_back(line);
    }
    B = A;
    for (int e = 0; e < edits; ++e) {
        if (B.empty()) break;
        size_t pos = rng() % B.size();
        int op = static_cast<int>(rng() % 3);
        if (op == 0) {
            B[pos] = "MODIFIED " + B[pos];
        } else if (op == 1) {
            B.insert(B.begin() + static_cast<long>(pos), "INSERTED " + std::to_string(e));
        } else {
            B.erase(B.begin() + static_cast<long>(pos));
        }
    }
}

static bool selfTest() {
    std::mt19937 rng(12345);
    int fail = 0, cases = 0;

    // 邊界案例
    std::vector<std::vector<std::string>> fixed = {
        {},
        {{"a"}},
        {{"a", "b", "c"}},
        {{"x"}, {"y"}, {"x"}, {"y"}},
    };
    for (auto& A : fixed) {
        for (auto& B : fixed) {
            ++cases;
            std::vector<Op> dp = diffLcsDp(A, B);
            std::vector<Op> my = diffMyers(A, B);
            Stat sd = statOf(dp), sm = statOf(my);
            bool ok = applyOps(A, B, dp) && applyOps(A, B, my) && sd.del == sm.del && sd.ins == sm.ins;
            if (!ok) {
                ++fail;
                std::printf("FAIL (fixed) A=%zu B=%zu\n", A.size(), B.size());
            }
        }
    }

    // 隨機對拍
    for (int t = 0; t < 3000; ++t) {
        size_t na = rng() % 12, nb = rng() % 12;
        std::vector<std::string> A, B;
        for (size_t i = 0; i < na; ++i) A.push_back("v" + std::to_string(rng() % 4));
        for (size_t i = 0; i < nb; ++i) B.push_back("v" + std::to_string(rng() % 4));
        ++cases;
        std::vector<Op> dp = diffLcsDp(A, B);
        std::vector<Op> my = diffMyers(A, B);
        Stat sd = statOf(dp), sm = statOf(my);
        int lcs = lcsLengthRolling(A, B);
        int minEdits = static_cast<int>(A.size() + B.size()) - 2 * lcs;
        bool ok = applyOps(A, B, dp) && applyOps(A, B, my) &&
                  (static_cast<int>(sd.del + sd.ins) == minEdits) &&
                  (static_cast<int>(sm.del + sm.ins) == minEdits);
        if (!ok) {
            ++fail;
            std::printf("FAIL (random) na=%zu nb=%zu dp=%lld/%lld my=%lld/%lld lcs=%d\n",
                        na, nb, sd.del, sd.ins, sm.del, sm.ins, lcs);
            if (fail > 5) break;
        }
    }

    std::printf("self-test: %d cases, %d failures -> %s\n", cases, fail, fail == 0 ? "PASS" : "FAIL");
    return fail == 0;
}

static void bench(int n, int edits) {
    std::vector<std::string> A, B;
    makePair(n, edits, 2024u, A, B);

    auto t0 = Clock::now();
    std::vector<Op> dp = diffLcsDp(A, B);
    double dpMs = msSince(t0);

    t0 = Clock::now();
    std::vector<Op> my = diffMyers(A, B);
    double myMs = msSince(t0);

    Stat sd = statOf(dp), sm = statOf(my);
    int lcs = lcsLengthRolling(A, B);

    std::printf("N=%d lines, %d edits (B has %zu lines)\n", n, edits, B.size());
    std::printf("  LCS length            = %d\n", lcs);
    std::printf("  DP   (LCS table)      : %8.3f ms   del=%lld ins=%lld\n", dpMs, sd.del, sd.ins);
    std::printf("  Myers O(ND) greedy    : %8.3f ms   del=%lld ins=%lld\n", myMs, sm.del, sm.ins);
    std::printf("  speedup (DP/Myers)    : %8.2fx\n", myMs > 0 ? dpMs / myMs : 0.0);
}

static void runFile(const char* pa, const char* pb, const std::string& mode) {
    std::vector<std::string> A = splitLines(readFile(pa));
    std::vector<std::string> B = splitLines(readFile(pb));
    if (mode == "dp") {
        printDiff(A, B, diffLcsDp(A, B));
    } else {
        printDiff(A, B, diffMyers(A, B));
    }
}

int main(int argc, char** argv) {
    std::string cmd = argc > 1 ? argv[1] : "demo";
    if (cmd == "demo") {
        demo();
    } else if (cmd == "selftest") {
        return selfTest() ? 0 : 1;
    } else if (cmd == "bench") {
        int n = argc > 2 ? std::atoi(argv[2]) : 2000;
        int d = argc > 3 ? std::atoi(argv[3]) : 40;
        bench(n, d);
    } else if (cmd == "file") {
        if (argc < 4) {
            std::printf("usage: diff_main file <a.txt> <b.txt> [dp|myers]\n");
            return 1;
        }
        runFile(argv[2], argv[3], argc > 4 ? argv[4] : "myers");
    } else {
        std::printf("usage: diff_main [demo|selftest|bench N D|file a b [dp|myers]]\n");
        return 1;
    }
    return 0;
}
