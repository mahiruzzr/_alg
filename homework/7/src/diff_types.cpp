#include "diff_types.h"

#include <cstdio>
#include <fstream>
#include <sstream>

std::vector<std::string> splitLines(const std::string& text) {
    std::vector<std::string> lines;
    std::string cur;
    for (char c : text) {
        if (c == '\n') {
            if (!cur.empty() && cur.back() == '\r') cur.pop_back();
            lines.push_back(cur);
            cur.clear();
        } else {
            cur.push_back(c);
        }
    }
    if (!cur.empty()) {
        if (!cur.empty() && cur.back() == '\r') cur.pop_back();
        lines.push_back(cur);
    }
    return lines;
}

std::string readFile(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return {};
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

bool applyOps(const std::vector<std::string>& a,
              const std::vector<std::string>& b,
              const std::vector<Op>& ops) {
    size_t ai = 0, bi = 0;
    std::vector<std::string> out;
    out.reserve(b.size());
    for (const Op& op : ops) {
        switch (op.kind) {
            case OpKind::Equal:
                if (ai >= a.size() || bi >= b.size()) return false;
                if (a[ai] != b[bi]) return false;
                out.push_back(a[ai]);
                ++ai;
                ++bi;
                break;
            case OpKind::Delete:
                if (ai >= a.size()) return false;
                ++ai;
                break;
            case OpKind::Insert:
                if (bi >= b.size()) return false;
                out.push_back(b[bi]);
                ++bi;
                break;
        }
    }
    return ai == a.size() && bi == b.size() && out == b;
}

static std::string hunkHeader(size_t aStart, size_t aCount, size_t bStart, size_t bCount) {
    char buf[128];
    std::snprintf(buf, sizeof(buf), "@@ -%zu,%zu +%zu,%zu @@", aStart + 1, aCount, bStart + 1, bCount);
    return std::string(buf);
}

void printDiff(const std::vector<std::string>& a,
               const std::vector<std::string>& b,
               const std::vector<Op>& ops) {
    const size_t CONTEXT = 3;

    // 先標記每個指令對應的行號，並找出「變動區塊」的邊界
    struct Item {
        Op op;
        size_t aLine;  // 0-based，Equal/Delete 有效
        size_t bLine;  // 0-based，Equal/Insert 有效
    };
    std::vector<Item> items;
    items.reserve(ops.size());
    size_t ai = 0, bi = 0;
    for (const Op& op : ops) {
        Item it{op, 0, 0};
        if (op.kind != OpKind::Insert) it.aLine = ai;
        if (op.kind != OpKind::Delete) it.bLine = bi;
        if (op.kind == OpKind::Equal || op.kind == OpKind::Delete) ++ai;
        if (op.kind == OpKind::Equal || op.kind == OpKind::Insert) ++bi;
        items.push_back(it);
    }

    // 收集變動點
    std::vector<size_t> changed;
    for (size_t i = 0; i < items.size(); ++i)
        if (items[i].op.kind != OpKind::Equal) changed.push_back(i);

    if (changed.empty()) {
        std::printf("--- a\n+++ b\n@@ files are identical @@\n");
        return;
    }

    // 合併重疊的 hunk
    std::vector<std::pair<size_t, size_t>> hunks;  // [start,end) 於 items
    for (size_t c : changed) {
        size_t s = c > CONTEXT ? c - CONTEXT : 0;
        size_t e = c + CONTEXT + 1;
        if (e > items.size()) e = items.size();
        if (!hunks.empty() && s <= hunks.back().second) {
            hunks.back().second = e;
        } else {
            hunks.emplace_back(s, e);
        }
    }

    std::printf("--- a\n+++ b\n");
    for (auto& h : hunks) {
        size_t aStart = 0, bStart = 0;
        for (size_t i = 0; i < h.first; ++i) {
            if (items[i].op.kind != OpKind::Insert) ++aStart;
            if (items[i].op.kind != OpKind::Delete) ++bStart;
        }
        size_t aCount = 0, bCount = 0;
        for (size_t i = h.first; i < h.second; ++i) {
            if (items[i].op.kind != OpKind::Insert) ++aCount;
            if (items[i].op.kind != OpKind::Delete) ++bCount;
        }
        std::printf("%s\n", hunkHeader(aStart, aCount, bStart, bCount).c_str());
        for (size_t i = h.first; i < h.second; ++i) {
            const Item& it = items[i];
            switch (it.op.kind) {
                case OpKind::Equal: std::printf(" %s\n", a[it.aLine].c_str()); break;
                case OpKind::Delete: std::printf("-%s\n", a[it.aLine].c_str()); break;
                case OpKind::Insert: std::printf("+%s\n", b[it.bLine].c_str()); break;
            }
        }
    }
}
