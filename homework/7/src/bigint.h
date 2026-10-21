#pragma once

// 極簡大整數（僅支援非負整數），base 1e9，小端序存放
// 目的：示範 C(n,k) 在 n 變大時，64 位元整數會溢位，必須改用大數 +
//       動態規劃（Pascal 公式）才能精確計算。
#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>

class BigUInt {
public:
    static constexpr uint32_t BASE = 1000000000u;  // 1e9
    std::vector<uint32_t> d;

    BigUInt() : d(1, 0) {}

    explicit BigUInt(uint64_t v) {
        while (v > 0) {
            d.push_back(static_cast<uint32_t>(v % BASE));
            v /= BASE;
        }
        if (d.empty()) d.push_back(0);
    }

    void trim() {
        while (d.size() > 1 && d.back() == 0) d.pop_back();
    }

    bool isZero() const { return d.size() == 1 && d[0] == 0; }

    BigUInt& operator+=(const BigUInt& o) {
        const size_t n = std::max(d.size(), o.d.size());
        d.resize(n, 0);
        uint64_t carry = 0;
        for (size_t i = 0; i < n; ++i) {
            uint64_t cur = static_cast<uint64_t>(d[i]) + carry + (i < o.d.size() ? o.d[i] : 0);
            if (cur >= BASE) {
                cur -= BASE;
                carry = 1;
            } else {
                carry = 0;
            }
            d[i] = static_cast<uint32_t>(cur);
        }
        if (carry) d.push_back(1);
        return *this;
    }

    BigUInt& operator*=(const BigUInt& o) {
        std::vector<uint32_t> r(d.size() + o.d.size() + 2, 0);
        for (size_t i = 0; i < d.size(); ++i) {
            uint64_t carry = 0;
            for (size_t j = 0; j < o.d.size(); ++j) {
                uint64_t cur = static_cast<uint64_t>(d[i]) * o.d[j] + r[i + j] + carry;
                r[i + j] = static_cast<uint32_t>(cur % BASE);
                carry = cur / BASE;
            }
            size_t idx = i + o.d.size();
            uint64_t cur = static_cast<uint64_t>(r[idx]) + carry;
            r[idx] = static_cast<uint32_t>(cur % BASE);
            uint64_t c2 = cur / BASE;
            size_t k2 = idx + 1;
            while (c2 > 0 && k2 < r.size()) {
                uint64_t s = static_cast<uint64_t>(r[k2]) + c2;
                r[k2] = static_cast<uint32_t>(s % BASE);
                c2 = s / BASE;
                ++k2;
            }
        }
        d.swap(r);
        trim();
        return *this;
    }

    // 除以小整數（必須整除；回傳餘數以便驗證）
    BigUInt divSmall(uint32_t m, uint32_t* remainder = nullptr) const {
        BigUInt q;
        q.d.assign(d.size(), 0);
        uint64_t rem = 0;
        for (size_t i = d.size(); i-- > 0;) {
            uint64_t cur = rem * BASE + d[i];
            q.d[i] = static_cast<uint32_t>(cur / m);
            rem = cur % m;
        }
        q.trim();
        if (remainder) *remainder = static_cast<uint32_t>(rem);
        return q;
    }

    std::string str() const {
        std::string s = std::to_string(d.back());
        for (size_t i = d.size() - 1; i-- > 0;) {
            std::string part = std::to_string(d[i]);
            s.append(9 - part.size(), '0');
            s += part;
        }
        return s;
    }
};
