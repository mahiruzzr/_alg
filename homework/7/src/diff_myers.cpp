#include "diff_myers.h"

#include <algorithm>
#include <climits>

namespace {

constexpr int kNone = INT_MIN;

// 依 Myers 的貪婪規則挑出「上一個落點」所在的對角線：
//   prevK == k+1  -> 上一個動作是「往下」(insert B)
//   prevK == k-1  -> 上一個動作是「往右」(delete A)
// get(kk) 必須回傳 V_{d-1}[kk]（該對角線上最遠的 x），-1 代表不可達。
// 為了保證路徑不越界，會先檢查兩種分支是否合法，非法就跳過。
template <class Getter>
int choosePrevK(const Getter& get, int d, int k, int N, int M) {
    const bool hasDown = (k != d);   // 需要 V_{d-1}[k+1]
    const bool hasRight = (k != -d); // 需要 V_{d-1}[k-1]
    const int vDown = hasDown ? get(k + 1) : -1;
    const int vRight = hasRight ? get(k - 1) : -1;

    const int downX = vDown;      // 往下不動 x
    const int rightX = vRight + 1; // 往右 x+1
    const bool downOk = hasDown && vDown >= 0 && downX <= N && (downX - k) >= 0 && (downX - k) <= M;
    const bool rightOk = hasRight && vRight >= 0 && vRight < N && (rightX - k) >= 0 && (rightX - k) <= M;

    if (downOk && rightOk) return (downX >= rightX) ? (k + 1) : (k - 1);
    if (downOk) return k + 1;
    if (rightOk) return k - 1;
    return kNone;
}

struct MyersCore {
    int N = 0, M = 0, D = 0;
    int off = 0;
    std::vector<int> V;                  // 滾動中的 V（每一輪就地更新）
    std::vector<std::vector<int>> trace;  // trace[d][(k+d)/2] = V_d[k]，k = -d, -d+2, ..., d

    void forward(const std::vector<std::string>& A, const std::vector<std::string>& B) {
        N = static_cast<int>(A.size());
        M = static_cast<int>(B.size());
        const int maxD = N + M;
        off = maxD + 1;
        V.assign(2 * maxD + 3, -1);
        trace.clear();
        trace.reserve(static_cast<size_t>(std::min(maxD, 4096)) + 1);
        D = -1;

        for (int d = 0; d <= maxD && D < 0; ++d) {
            // 本輪讀取的是上一輪 (d-1) 的 V；parity 保證不會被本輪覆寫
            auto get = [&](int kk) -> int { return V[off + kk]; };

            for (int k = -d; k <= d; k += 2) {
                int x = 0, y = 0;
                if (d == 0) {
                    x = 0;
                    y = 0;
                } else {
                    const int prevK = choosePrevK(get, d, k, N, M);
                    if (prevK == kNone) {
                        V[off + k] = -1;
                        continue;
                    }
                    if (prevK == k + 1) {
                        x = V[off + k + 1];
                    } else {
                        x = V[off + k - 1] + 1;
                    }
                    y = x - k;
                }

                // 沿對角線貪婪地延伸（snake）：A[x] == B[y] 就免費走一步
                while (x < N && y < M && A[x] == B[y]) {
                    ++x;
                    ++y;
                }
                V[off + k] = x;
                if (x >= N && y >= M) {
                    D = d;
                    break;
                }
            }

            std::vector<int> snap(static_cast<size_t>(d) + 1, -1);
            for (int k = -d; k <= d; k += 2) snap[(k + d) / 2] = V[off + k];
            trace.push_back(std::move(snap));
        }
    }

    std::vector<Op> backtrack() {
        std::vector<Op> rev;
        int x = N, y = M;
        for (int d = D; d >= 1; --d) {
            const std::vector<int>& Vprev = trace[d - 1];
            auto get = [&](int kk) -> int { return Vprev[(kk + (d - 1)) / 2]; };
            const int k = x - y;
            const int prevK = choosePrevK(get, d, k, N, M);
            if (prevK == kNone) break;  // 不應該發生，防御性處理
            const int prevX = get(prevK);
            const int prevY = prevX - prevK;

            if (prevK == k + 1) {
                // 上一個動作是「往下」：吃掉 B[prevY]
                while (x > prevX && y > prevY + 1) {
                    --x;
                    --y;
                    rev.push_back(Op{OpKind::Equal, x, y});
                }
                --y;
                rev.push_back(Op{OpKind::Insert, -1, y});
            } else {
                // 上一個動作是「往右」：吃掉 A[prevX]
                while (x > prevX + 1 && y > prevY) {
                    --x;
                    --y;
                    rev.push_back(Op{OpKind::Equal, x, y});
                }
                --x;
                rev.push_back(Op{OpKind::Delete, x, -1});
            }
            x = prevX;
            y = prevY;
        }

        // d == 0：剩下的都是起點的共同前綴（對角線）
        while (x > 0 && y > 0) {
            --x;
            --y;
            rev.push_back(Op{OpKind::Equal, x, y});
        }
        std::reverse(rev.begin(), rev.end());
        return rev;
    }
};

}  // namespace

std::vector<Op> diffMyers(const std::vector<std::string>& a, const std::vector<std::string>& b) {
    MyersCore core;
    core.forward(a, b);
    return core.backtrack();
}

int myersEditDistance(const std::vector<std::string>& a, const std::vector<std::string>& b) {
    MyersCore core;
    core.forward(a, b);
    return core.D;
}
