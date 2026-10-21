#pragma once

#include <cstdint>
#include <string>
#include <vector>

// 一個差異編輯指令（edit script）
enum class OpKind : uint8_t {
    Equal = 0,   // A[aIndex] == B[bIndex]，兩邊都保留
    Delete = 1,  // 刪掉 A[aIndex]
    Insert = 2,  // 插入 B[bIndex]
};

struct Op {
    OpKind kind;
    int aIndex;
    int bIndex;
};

// 把整份文字切成「行」（去掉行尾 \n / \r），以行為 diff 的比較單位
std::vector<std::string> splitLines(const std::string& text);

// 讀檔（讀不到回傳空字串）
std::string readFile(const std::string& path);

// 把編輯指令套回 A，驗證是否能還原成 B；回傳 false 表示指令不合法
bool applyOps(const std::vector<std::string>& a,
              const std::vector<std::string>& b,
              const std::vector<Op>& ops);

// 產生類似 unified diff 的輸出
void printDiff(const std::vector<std::string>& a,
               const std::vector<std::string>& b,
               const std::vector<Op>& ops);
