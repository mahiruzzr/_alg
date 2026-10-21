# 文字問題的兩種解法：diff（兩檔案差異比對）
### 動態規劃（LCS 表格） vs 非動態規劃（Myers O(ND)）

> 附第二個案例：**C(n,k) 組合數**（遞迴 vs 記憶化/建表 DP vs 閉式解），
> 以及 blast / grep / Boyer–Moore / Aho–Corasick 的 DP ↔ 非 DP 對照表。

---

## 0. TL;DR

| | 動態規劃（LCS） | 非動態規劃（Myers） |
|---|---|---|
| 核心 | 填滿 `dp[i][j]` 表格，再回溯 | 在編輯圖上貪婪地找「最遠可達點」 |
| 時間 | `O(N·M)`，**與差異大小無關** | `O((N+M)·D)`，`D` = 編輯距離 |
| 空間 | `O(N·M)`（本實作用 `uint16_t` 減半） | `O(D²)`（線性空間改良版 `O(N+M)`） |
| 保證 | 最小編輯脚本 | 也是最小編輯脚本（Myers 定理） |
| 強項 | 差異很大、檔案不大 | 差異很小、檔案很大（實務常態） |

實測（本機 MinGW g++ 15.2, `-O2`，單位 ms）：

| 案例 | DP | Myers | 誰快 |
|---|---:|---:|---|
| 2000 行，改 40 處 | 23.4 | 0.26 | Myers **91×** |
| 5000 行，改 100 處 | 154.8 | 0.50 | Myers **313×** |
| 2000 行，改 400 處 | 23.6 | 3.42 | Myers 6.9× |
| 5000 行，改 500 處 | 191.9 | 6.95 | Myers 28× |
| 1000 行，每行都改 | 5.1 | 9.1 | **DP 1.8×** |
| 2000 行，每行都改 | 15.4 | 32.1 | **DP 2.1×** |

兩者輸出的 `del/ins` 數量在所有測試中完全相同（都是最小解），
差別只在「用什麼策略找到它」。

> 數據為代表性單次測值（MinGW g++ 15.2 / `-O2` / Windows），
> 絕對值會隨機器與快取波動，但**趨勢**（相似檔 Myers 大勝、差異大 DP 勝）穩定重現。

---

## 1. 問題定義

給定兩份文字檔（以「行」為單位）：

```
A = [a0, a1, ..., a(N-1)]     N 行
B = [b0, b1, ..., b(M-1)]     M 行
```

允許三種動作，成本分別是：

| 動作 | 意義 | 成本 |
|---|---|---|
| Equal | `A[i] == B[j]`，保留 | 0 |
| Delete | 刪掉 `A[i]` | 1 |
| Insert | 插入 `B[j]` | 1 |

**目標**：找一組動作（edit script），把 A 變成 B，且總成本最小。
這就是 `diff`、`git diff`、`patch` 在做的事。

等價說法：找出 A、B 的**最長共同子序列** LCS，長度 `L`。
保留 `L` 行，剩下 `N-L` 行刪掉、`M-L` 行插入，成本

```
cost = (N - L) + (M - L) = N + M - 2L
```

所以「**最小 diff**」⇔「**最大 LCS**」。

---

## 2. 解法一：動態規劃（LCS 表格）

### 2.1 為什麼這是動態規劃

問題具備 DP 的兩個必要條件：

1. **最佳子結構（optimal substructure）**
   `A[0..i)` 與 `B[0..j)` 的 LCS，若 `A[i-1] == B[j-1]`，一定可以把這對接在
   `A[0..i-1)`、`B[0..j-1)` 的 LCS 後面；否則答案必是「去掉 A 的最後一個」
   或「去掉 B 的最後一個」兩者之一。
2. **重疊子問題（overlapping subproblems）**
   `(i-1, j)` 與 `(i, j-1)` 會共同需要 `(i-1, j-1)` 的答案；naive 遞迴會重算
   指數次，因此把答案**建表**保存。

### 2.2 遞迴式

```
dp[0][j] = 0,  dp[i][0] = 0

dp[i][j] = dp[i-1][j-1] + 1                     if A[i-1] == B[j-1]
         = max(dp[i-1][j], dp[i][j-1])          otherwise
```

`dp[i][j]` 就是 `LCS(A[0..i), B[0..j))` 的長度。

以 `A = [a,b,c]`、`B = [a,c]` 為例：

```
        ""   a    c
  ""  [  0   0    0 ]
  a   [  0   1    1 ]
  b   [  0   1    1 ]
  c   [  0   1    2 ]   <- dp[3][2] = 2，LCS = "a c"
```

### 2.3 回溯（backtrack）產生 edit script

從右下角 `(N, M)` 往回走：

```
if A[i-1] == B[j-1]      -> Equal(A[i-1])，i--, j--
else if dp[i-1][j] >= dp[i][j-1]
                         -> Delete(A[i-1])，i--
else                     -> Insert(B[j-1])，j--
```

走完後反轉，就得到由左到右的編輯脚本。
（`>=` 或 `>` 只影響「同時可刪可插」時的選擇，兩者都是最小解。）

### 2.4 複雜度

| 項目 | 複雜度 | 說明 |
|---|---|---|
| 時間 | `O(N·M)` | 每一格算一次 |
| 空間（本實作） | `O(N·M)` | `uint16_t` 每格 2 bytes；LCS ≤ 65535 |
| 只算長度 | `O(min(N,M))` | 滾動陣列 |
| 要回溯又要省空間 | `O(min(N,M))` | Hirschberg 分治（時間仍 `O(N·M)`） |

**關鍵缺點**：不管兩檔案多像，`dp` 表都要填滿 `N×M` 格。
5000 行 × 5000 行 = 2500 萬格（50 MB）；5 萬行就是 5 GB，直接不可行。

### 2.5 程式（`src/diff_dp.cpp`）

```cpp
for (size_t i = 1; i <= N; ++i)
    for (size_t j = 1; j <= M; ++j) {
        if (a[i-1] == b[j-1])
            at(i, j) = at(i-1, j-1) + 1;
        else
            at(i, j) = std::max(at(i-1, j), at(i, j-1));
    }
```

### 2.6 實測

```
$ build/diff_main.exe bench 5000 100
N=5000 lines, 100 edits (B has 5001 lines)
  LCS length            = 4935
  DP   (LCS table)      :  154.788 ms   del=65 ins=66
  Myers O(ND) greedy    :    0.495 ms   del=65 ins=66
  speedup (DP/Myers)    :  312.89x
```

---

## 3. 解法二：非動態規劃（Myers O(ND)）

參考：Eugene W. Myers, *An O(ND) Difference Algorithm and Its Variations*,
Algorithmica 1(2), 1986. （git 的預設 diff 就是這個家族）

### 3.1 編輯圖（edit graph）

把比對過程畫成一座格子：

```
        B:  a    b    c    d
      +----+----+----+----+
  ""  |    |    |    |    |
      +----+----+----+----+
  a   |    | \  |    |    |      \ = 對角線：A[i]==B[j]，免費
      +----+----+----+----+      → = 刪除 A[i]，成本 1
  b   |    |    | \  |    |      ↓ = 插入 B[j]，成本 1
      +----+----+----+----+
  c   |    |    |    | \  |
      +----+----+----+----+
```

- 從左上 `(0,0)` 走到右下 `(N,M)`。
- 走對角線（兩邊相同）成本 0；往右（刪 A）或往下（插 B）成本 1。
- **最短路徑的長度就是最小編輯距離 D**，路徑本身就是 edit script。

### 3.2 對角線 k 與 D-path

定義 `k = x - y`（目前在哪一條對角線），`d` = 目前已經走的非對角線步數。
Myers 的關鍵觀察：

> 對每一條對角線 k，只需要記住「走 d 步之後，能到達的最大 x」
> （稱為 furthest-reaching point，記在 `V[k]`）。
> 因為在編輯圖上，走得越遠越有利 —— 這就是貪婪的依據。

`V[k]` 每輪的遞推：

```
V[k] = 從 V[k-1]+1（往右，刪除）或 V[k+1]（往下，插入）中選 x 較大者
       然後沿對角線一直走，直到 A[x] != B[y] 或撞到邊界
```

那個「沿對角線一直走」的動作叫 **snake**，是本演算法效率的來源：
連續相同的行完全不花成本、直接跳過。

```
d=0:  V[0]  = 0 + snake(共同前綴)
d=1:  k=-1, +1
d=2:  k=-2, 0, +2
...
直到某條對角線的 x >= N 且 y >= M，此時的 d 就是最小編輯距離 D。
```

### 3.3 為何不需要 DP 表格

DP 是「**每一格都算**」，Myers 是「**每一輪只保留每條對角線的最遠點**」。
它利用的是編輯圖的單調性（往右/往下不會讓路徑變短），
所以不需要知道「所有 (i,j) 的答案」，只需要「到目前為止每條對角線能走多遠」。

代價是：**當 D 很大時**（兩檔案幾乎完全不同），要跑的輪數 `d = 1..D`
加上每輪 `O(d)` 條對角線，總共 `O(D²)`，而 `D` 可達 `N+M`，
因此最壞情況是 `O((N+M)²)` —— 這時反而比 DP 慢（見第 4 節實測）。

### 3.4 回溯

每一輪的 `V` 快照存起來（`trace[d]`），從 `(N, M)` 往回推：

```
k = x - y
prevK = (k == -d || (k != d && V_{d-1}[k-1] < V_{d-1}[k+1])) ? k+1 : k-1
```

`prevK == k+1` ⇒ 上一步是「往下」（Insert）；`prevK == k-1` ⇒ 「往右」（Delete）。
把 snake 上的點補成 Equal，反轉即得 edit script。

本實作為了正確處理邊界，會先過濾「會走出格子」的分支
（`src/diff_myers.cpp` 的 `choosePrevK`），並用 3016 組隨機/邊界測資與
DP 對拍驗證（見第 7 節）。

### 3.5 複雜度

| 項目 | 複雜度 |
|---|---|
| 時間 | `O((N+M)·D)`，`D` = 最小編輯距離 |
| 空間（本實作，存快照回溯） | `O(D²)` |
| 空間（線性空間改良：middle snake 分治） | `O(N+M)` |
| 最佳情況（兩檔相同） | `O(N+M)`，`D=0` |
| 最壞情況（完全不同） | `O((N+M)²)`，`D=N+M` |

### 3.6 程式（`src/diff_myers.cpp` 核心）

```cpp
for (int d = 0; d <= maxD; ++d) {
    for (int k = -d; k <= d; k += 2) {
        int x = (k == -d || (k != d && V[k-1] < V[k+1])) ? V[k+1]      // 往下
                                                        : V[k-1] + 1;  // 往右
        int y = x - k;
        while (x < N && y < M && A[x] == B[y]) { ++x; ++y; }  // snake
        V[k] = x;
        if (x >= N && y >= M) { D = d; break; }
    }
}
```

### 3.7 實測

```
$ build/diff_main.exe bench 2000 40
N=2000 lines, 40 edits (B has 2005 lines)
  LCS length            = 1976
  DP   (LCS table)      :   23.411 ms   del=24 ins=29
  Myers O(ND) greedy    :    0.256 ms   del=24 ins=29
  speedup (DP/Myers)    :    91.45x
```

---

## 4. 兩者比較

### 4.1 原理層面

| 面向 | LCS 動態規劃 | Myers O(ND) |
|---|---|---|
| 思考方式 | 「**所有**子問題的答案都算出來」 | 「只追蹤**目前為止**每條對角線的最遠點」 |
| 決策方式 | 比較三種來源，取 max（完整資訊） | 貪婪 + snake（區域資訊 + 單調性） |
| 是否最小解 | 是 | 是（Myers 定理保證） |
| 對輸入敏感度 | 只看 `N、M` | 看 `N、M、D` |
| 實作難度 | 低（10 行核心） | 中（對角線索引、回溯容易寫錯） |
| 可平行/可增量 | 較難 | 容易（Myers 有 linear-space、patience 等變體） |

### 4.2 複雜度層面

```
DP:     O(N·M)              不管差多少
Myers:  O((N+M)·D)          差得越少越快；D ≈ N+M 時退化為 O((N+M)²)
```

交叉點大約在 `D ≈ N·M / (N+M) ≈ min(N,M)`：
- `D << min(N,M)`（檔案相似）→ Myers 大勝，可差 1~2 個數量級。
- `D ≈ min(N,M)`（大量差異）→ DP 勝（常數小、記憶體存取連續）。

### 4.3 實務選擇

- **版本控制 / 編輯器 / patch**：檔案通常只改幾行 → 用 Myers（或 patience/histogram 變體）。
- **兩份完全不同的文件、或需要 LCS 長度/相似度**：用 DP（或 Hirschberg）。
- **檔案很大又不想花 `O(N·M)` 記憶體**：Myers 線性空間版，或先做前後綴裁剪（trim）再 diff。
- **需要 `diff` 以外的東西**（例如同時要 LCS 長度、編輯距離、相似度矩陣）：DP 表格可直接重用。

> 小技巧：實務上的 diff 幾乎都會先「修剪共同前後綴」，
> 這一步對兩種演算法都有幫助，但對 Myers 尤其明顯（直接少掉大段 snake）。

---

## 5. 第二個案例：C(n,k)（n 個取 k 個）

### 5.1 四種寫法

| 寫法 | 類別 | 遞迴式 / 公式 | 時間 | 空間 |
|---|---|---|---|---|
| 純遞迴 | 非 DP | `C(n,k)=C(n-1,k-1)+C(n-1,k)` | `O(2^n)`（實際 ≈ 2.9·C(n,k) 次呼叫） | `O(n)` 堆疊 |
| top-down 記憶化 | **DP** | 同上 + memo 表 | `O(n·k)` | `O(n·k)` |
| bottom-up 建表 | **DP** | Pascal 三角形，1-D 滾動 | `O(n·k)` | `O(k)` |
| 連乘閉式解 | 非 DP | `C(n,k)=∏(n-k+i)/i` | `O(k)` 次大數乘除 | `O(位數)` |
| double 直算 | 非 DP | `n!/(k!(n-k)!)` | `O(n)` | `O(1)`，**但會算錯** |

### 5.2 為什麼「純遞迴」是指數時間

```
C(5,2)
├── C(4,1)
│   ├── C(3,0)
│   └── C(3,1) ── ...
└── C(4,2)
    ├── C(3,1)  <-- 重複！
    └── C(3,2)  <-- 又重複！
```

`C(3,1)` 被算了兩次、`C(2,1)` 被算了三次……重疊子問題沒有被保存，
複雜度退化為 `O(2^n)`。本機實測：

```
C(30,15) = 155117520   calls = 445,962,869   1.86 s
C(36,18)                calls = 26,270,128,499  71 s
C(60,30)                約需 3×10^17 次呼叫（不可能跑完）
```

### 5.3 DP 版

```cpp
// top-down
memo[n][k] = cnk(n-1, k-1) + cnk(n-1, k);
// bottom-up（1-D）
for (int i = 1; i <= n; ++i)
    for (int j = min(i, k); j >= 1; --j)
        dp[j] += dp[j-1];      // dp[j] = C(i, j)
```

同一題 `C(60,30)`：`929` 次計算、`0.01 ms`，差距是天文數字。

### 5.4 精度陷阱（對應參考教材的 JS 案例）

`double` 只有 53 bits 有效位元（約 15~17 位十進位），
`60!` 遠超這個範圍，於是最後除法會出現「看起來很接近、但答案是錯的」：

```
C(60,30) 正確 = 118264581564861424
double 算成   = 118264581564861472   （JS 版：...470）
```

而且 `unsigned long long` 也不夠：`C(75,37)` 已經需要 22 位數，
`C(1000,500)` 有 300 位數。所以要嘛用大數（本專案 `src/bigint.h`），
要嘛像競賽程式一樣在 `mod 1e9+7` 下用 DP 加法（DP 只做加法，天生適合取模）。

### 5.5 實測

```
== 3. DP: bottom-up tabulation (1-D array) ==
   C(  60,  30) = 118264581564861424      0.002 ms  (time O(n*k), space O(k))  exact
   C( 120,  60) = 2093244173541933552     0.005 ms  OVERFLOW -> needs BigUInt

== 4. Non-DP: closed-form product ==
   C( 120,  60) = 96614908840363322603893139521372656   0.016 ms  (O(k) mul/div)
   C(1000, 500) = 27028824094543656951561469362...6320  0.343 ms  (O(k) mul/div)

== 6. DP + big integers ==
   C(1000, 500) = 27028824094543656951561469362...6320 50.297 ms  (digits=300)
```

有趣的是：**大數版本反而是「非 DP 的閉式解」比較快**（0.34 ms vs 50 ms），
因為它只做 `k` 次乘除，而 DP 要做 `n·k` 次大數加法。
但閉式解每一步都要求「整除」、且不能取模；DP 只做加法、可取模、可重複使用整張表。
**所以「DP 一定比較好」是錯的，重點是問題結構與限制。**

---

## 6. 其他候選問題：DP ↔ 非 DP 對照

| 問題 | 動態規劃解法 | 非 DP 解法 | DP 複雜度 | 非 DP 複雜度 | 備註 |
|---|---|---|---|---|---|
| **diff**（本專案） | LCS 表格 + 回溯 | Myers 貪婪 + snake | `O(N·M)` | `O((N+M)·D)` | 相似檔用 Myers，差異大用 DP |
| **blast** DNA 比對 | Needleman–Wunsch / Smith–Waterman | seed-and-extend（k-mer 索引 + HSP 延伸） | `O(n·m)` | 實務近線性，但**啟發式、不保證最佳** | DP 保證最佳；BLAST 快但可能漏 |
| **grep** 正則 | Thompson NFA 模擬 / bit-parallel Shift-And | 回溯式引擎（PCRE） | `O(n·m)` 保證 | 最壞指數（catastrophic backtracking） | 回溯引擎支援 backreference，automaton 不支援 |
| **單字搜尋** | KMP 的 π 表（前綴函數 DP）/ Shift-And | Boyer–Moore（壞字元 + 好後綴） | `O(n+m)` 保證 | 平均 `O(n/m)`，最壞 `O(n·m)` | BM 在自然文字上最快（跳躍）；KMP 最壞有保證 |
| **敏感詞過濾** | 每個 pattern 各做一次 KMP/DP | Aho–Corasick 自動機（Trie + failure link） | `O(k·n + Σ|p|)` | `O(n + Σ|p| + hits)` | 模式越多，AC 優勢越大 |
| **C(n,k)** | Pascal 建表 / 記憶化 | 連乘閉式解（+ 大數） | `O(n·k)` | `O(k)` 次大數運算 | DP 只做加法，適合取模 |

補充說明：

- **BLAST**：先把序列切成 k-mer 建索引（雜湊），命中後往兩側延伸（X-drop）。
  「seed」對應 diff 的 snake，「extend」對應貪婪延伸 —— 思想其實和 Myers 很像，
  都是「先找確定相同的小片段，再往外長」，只是不保證全域最佳。
- **Aho–Corasick**：把 k 個 pattern 合成一棵 Trie，再用 BFS 建 failure link，
  掃一次文本就能同時回報所有命中。嚴格說 failure link 的建構也是「用已知推未知」
  的表格法，但**匹配階段是單次線性掃描**，和「每個 pattern 各跑一次 DP」有本質差異。
- **Boyer–Moore**：從 pattern 尾端往左比，利用壞字元表/好後綴表決定「可以跳多遠」，
  平均只要看 `n/m` 個字元；最壞情況（如 `aaaa...a`）仍需 `O(n·m)`。
- **grep**：實務上的 `grep` 對「固定字串」用 BM 家族（memchr/SIMD），
  對 regex 用 NFA/DFA；PCRE 這類回溯引擎在 `(a+)+b` 這種 pattern 上會指數爆炸。

---

## 7. 正確性驗證

1. **C++ 內建對拍**（`diff_main selftest`）：
   - 4×4 邊界案例（空檔、單行、全同、交錯）＋ 3000 組隨機輸入。
   - 檢查：edit script 套回 A 必須等於 B；`del+ins` 必須等於 `N+M-2·LCS`。
   - 結果：`3016 cases, 0 failures -> PASS`。

2. **獨立驗證**（`python verify.py`）：
   - `C(n,k)` 與 Python `math.comb` 比對（含 300 位數的 `C(1000,500)`）。
   - diff 輸出解析成 unified diff 後**重新套用**，必須還原 B；
     且 `+/-` 行數必須等於 Python 獨立計算的 `N+M-2·LCS`。
   - 結果：`80 random pairs OK` ＋ `ALL VERIFIED`。

3. **兩種演算法互相比對**：所有測試中 DP 與 Myers 的 `del/ins` 完全相同。

---

## 8. 檔案結構與執行

```
text_dp_vs_nondp/
├── src/
│   ├── diff_types.h / diff_types.cpp   編輯指令、行切分、unified diff 輸出
│   ├── diff_dp.h    / diff_dp.cpp      【DP】LCS 表格 + 回溯
│   ├── diff_myers.h / diff_myers.cpp   【非 DP】Myers O(ND) + 回溯
│   ├── diff_main.cpp                   demo / selftest / bench / file
│   ├── bigint.h                        極簡大整數（base 1e9）
│   └── cnk.cpp                         C(n,k)：遞迴 / memo / 建表 / 閉式解
├── verify.py                           用 Python 獨立驗證
├── Makefile
├── run_all.bat                         一鍵編譯 + 執行全部展示
└── README.md
```

編譯與執行：

```bat
mingw32-make            :: 或直接跑 run_all.bat
build\diff_main.exe demo
build\diff_main.exe selftest
build\diff_main.exe bench 5000 100
build\diff_main.exe file a.txt b.txt myers
build\cnk.exe show
build\cnk.exe big 1000 500
python verify.py
```

需求：g++（C++17）＋ 選擇性 Python 3（驗證腳本）。

---

## 9. 參考資料

1. Eugene W. Myers, *An O(ND) Difference Algorithm and Its Variations*,
   Algorithmica 1(2):251–266, 1986.
2. 參考教材：<https://github.com/ccc115a/alg/tree/main/02-方法/08-動態規劃法>
   （C(n,k)、editDistance、Viterbi 等 DP 範例）
3. Hirschberg, *A linear space algorithm for computing maximal common subsequences*,
   CACM 18(6), 1975.
4. <https://en.wikipedia.org/wiki/Longest_common_subsequence>
5. <https://en.wikipedia.org/wiki/Diff#Algorithm>
