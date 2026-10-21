#pragma once

#include <vector>

#include "diff_types.h"

// ---------------------------------------------------------------------------
// 非動態規劃版 diff：Myers O(ND) 演算法
//
// 想法：把「A 變成 B」畫成一張編輯圖（edit graph）
//   x 軸 = A 的位置（往右 = 刪掉 A[x]）
//   y 軸 = B 的位置（往下 = 插入 B[y]）
//   對角線 = A[x] == B[y] 的匹配（免費）
//
// 一條最短路徑 = 一組最少的 insert/delete 動作。Myers 證明：
//   最短路徑一定會經過某條「對角線極遠點」，而且「最短編輯距離 D」
//   與「最大 D 路徑」一一對應。
//
// 演算法（forward pass，第 d 輪代表已經用了 d 次 insert/delete）：
//   對每個 k = -d, -d+2, ..., d（k = x - y 代表目前位置在第幾條對角線上）
//     x = 沿「往下」或「往右」移動一格後的 x
//     y = x - k
//     然後貪婪地沿對角線往前衝（"snake"）比對相同元素
//   V[k] = 這一輪結束時，該對角線上最遠的 x
//
// 不需要 DP 表格，靠「每輪只保留每條對角線的最遠點」+ 快照回溯。
// 時間 O((N+M) * D)，空間 O(D^2)（快照）；D 越小越快，檔案越像越快。
// ---------------------------------------------------------------------------

std::vector<Op> diffMyers(const std::vector<std::string>& a, const std::vector<std::string>& b);

// 回傳 Myers 的最小編輯距離 D（insert + delete 的數量）
int myersEditDistance(const std::vector<std::string>& a, const std::vector<std::string>& b);
