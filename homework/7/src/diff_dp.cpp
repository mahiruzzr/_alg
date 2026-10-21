#include "diff_dp.h"

#include <algorithm>

int lcsLengthRolling(const std::vector<std::string>& a, const std::vector<std::string>& b) {
    // 讓 b 是較短的那一邊，滾動陣列長度 = min(N, M)
    const std::vector<std::string>& A = a.size() >= b.size() ? a : b;
    const std::vector<std::string>& B = a.size() >= b.size() ? b : a;
    const size_t M = B.size();
    std::vector<int> prev(M + 1, 0), cur(M + 1, 0);
    for (size_t i = 1; i <= A.size(); ++i) {
        cur[0] = 0;
        for (size_t j = 1; j <= M; ++j) {
            if (A[i - 1] == B[j - 1])
                cur[j] = prev[j - 1] + 1;
            else
                cur[j] = std::max(prev[j], cur[j - 1]);
        }
        std::swap(prev, cur);
    }
    return static_cast<int>(prev[M]);
}

int lcsLengthTable(const std::vector<std::string>& a, const std::vector<std::string>& b) {
    const size_t N = a.size(), M = b.size();
    if (N == 0 || M == 0) return 0;
    // LCS 長度不超過 65535，用 uint16_t 省記憶體
    std::vector<uint16_t> dp((N + 1) * (M + 1), 0);
    auto at = [&](size_t i, size_t j) -> uint16_t& { return dp[i * (M + 1) + j]; };
    for (size_t i = 1; i <= N; ++i) {
        for (size_t j = 1; j <= M; ++j) {
            if (a[i - 1] == b[j - 1])
                at(i, j) = static_cast<uint16_t>(at(i - 1, j - 1) + 1);
            else
                at(i, j) = std::max(at(i - 1, j), at(i, j - 1));
        }
    }
    return at(N, M);
}

std::vector<Op> diffLcsDp(const std::vector<std::string>& a, const std::vector<std::string>& b) {
    const size_t N = a.size(), M = b.size();
    std::vector<Op> ops;
    if (N == 0 && M == 0) return ops;

    // 完整 DP 表格
    std::vector<uint16_t> dp((N + 1) * (M + 1), 0);
    auto at = [&](size_t i, size_t j) -> uint16_t& { return dp[i * (M + 1) + j]; };
    for (size_t i = 1; i <= N; ++i) {
        for (size_t j = 1; j <= M; ++j) {
            if (a[i - 1] == b[j - 1])
                at(i, j) = static_cast<uint16_t>(at(i - 1, j - 1) + 1);
            else
                at(i, j) = std::max(at(i - 1, j), at(i, j - 1));
        }
    }

    // 回溯：從 (N,M) 走回 (0,0)
    size_t i = N, j = M;
    while (i > 0 || j > 0) {
        if (i > 0 && j > 0 && a[i - 1] == b[j - 1]) {
            ops.push_back(Op{OpKind::Equal, static_cast<int>(i - 1), static_cast<int>(j - 1)});
            --i;
            --j;
        } else if (i > 0 && (j == 0 || at(i - 1, j) >= at(i, j - 1))) {
            ops.push_back(Op{OpKind::Delete, static_cast<int>(i - 1), -1});
            --i;
        } else {
            ops.push_back(Op{OpKind::Insert, -1, static_cast<int>(j - 1)});
            --j;
        }
    }
    std::reverse(ops.begin(), ops.end());
    return ops;
}
