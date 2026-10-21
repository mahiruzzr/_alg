#pragma once

#include <cstdint>
#include <vector>

#include "diff_types.h"

// ---------------------------------------------------------------------------
// 動態規劃版 diff
//
// 核心：LCS（最長共同子序列）動態規劃表
//   dp[i][j] = LCS(A[0..i-1], B[0..j-1]) 的長度
//   A[i-1] == B[j-1]  ->  dp[i][j] = dp[i-1][j-1] + 1
//   A[i-1] != B[j-1]  ->  dp[i][j] = max(dp[i-1][j], dp[i][j-1])
// 然後從 dp[N][M] 往回溯走出一條最長共同子序列，其餘就是 delete/insert。
//
// 時間 O(N*M)，空間 O(N*M)（本檔用 uint16_t 記憶體減半；Hirschberg 可降到 O(min(N,M))）
// ---------------------------------------------------------------------------

// LCS 長度（只算長度，記憶體 O(min(N,M)) 的滾動陣列）
int lcsLengthRolling(const std::vector<std::string>& a, const std::vector<std::string>& b);

// LCS 長度（完整表格版本，供驗證/對拍使用）
int lcsLengthTable(const std::vector<std::string>& a, const std::vector<std::string>& b);

// 回溯出編輯指令
std::vector<Op> diffLcsDp(const std::vector<std::string>& a, const std::vector<std::string>& b);
