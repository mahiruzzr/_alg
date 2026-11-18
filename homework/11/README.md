# 數值微積分與蒙地卡羅多維超體積積分系統 (Numerical Calculus & Monte Carlo Integration)

> ## 📢【AI 使用聲明 / AI Usage Declaration】
> **本專案所有程式碼（包括各模組、測試腳本、示範主程式）以及本份說明文件（README.md）完全由 AI (Google Antigravity / Gemini) 輔助設計、撰寫、簡化與最佳化。**  
> *This entire project (including all modules, test scripts, main demonstration, and this README.md) was designed, authored, simplified, and optimized with the assistance of AI (Google Antigravity / Gemini).*

---

## 📖 目錄 (Table of Contents)

1. [專案簡介與特色](#專案簡介與特色)
2. [數學原理與模組架構](#數學原理與模組架構)
   - [題目 1：單變數數值微分與積分](#題目-1單變數數值微分與積分)
   - [題目 2：單變數蒙地卡羅積分](#題目-2單變數蒙地卡羅積分)
   - [題目 3：多變數微分 (梯度) 與超體積數值積分](#題目-3多變數微分-梯度與超體積數值積分)
   - [題目 4：多變數蒙地卡羅超體積積分](#題目-4多變數蒙地卡羅超體積積分)
   - [題目 5：黎曼積分法函數 `integral(f, low, high)` 與「維度災難」](#題目-5黎曼積分法函數-integralf-low-high-與維度災難)
   - [題目 6：蒙地卡羅多變數積分 `mc_integral(f, low, high)` 與高維破局](#題目-6蒙地卡羅多變數積分-mc_integralf-low-high-與高維破局)
3. [第 5 題與第 6 題綜合實驗對比](#第-5-題與第-6-題綜合實驗對比)
4. [專案目錄結構](#專案目錄結構)
5. [快速開始與執行測試](#快速開始與執行測試)
6. [程式碼簡化與設計哲學 (Code Simplification)](#程式碼簡化與設計哲學-code-simplification)

---

## 專案簡介與特色

本專案實作了計算科學與應用數學中經典的數值微積分與隨機蒙地卡羅法演算法，涵蓋從基礎的單變數一階導數與定積分，到高維度的梯度向量、超長方體幾何超體積積分，並深入探討數值分析中最關鍵的課題——**黎曼網格法在面對超高維度時遭遇的「維度災難 (Curse of Dimensionality)」**，以及**蒙地卡羅法如何以維度無關的 $O(1/\sqrt{N})$ 收斂性實現高維積分破局**。

### 核心特性
- **遵循 Code Simplification 準則**：無多餘巢狀、職責單一、清晰命名、具備完整型別標記 (Type Hints)。
- **高數值穩定性與效能**：支援向量化批次加速計算，兼顧易讀性與運算效率。
- **全方位測試覆蓋**：附帶完整單元測試 (`unittest`) 與視覺化示範程式 (`main.py`)。

---

## 數學原理與模組架構

### 題目 1：單變數數值微分與積分
檔案：[`single_variable.py`](single_variable.py)

#### 1. 數值微分 (Numerical Differentiation)
利用泰勒展開式 (Taylor Expansion) 推導有限差分估計：
- **中心差分法 (Central Difference, 預設)**：
  $$f'(x) \approx \frac{f(x + h) - f(x - h)}{2h}, \quad \text{截斷誤差 } O(h^2)$$
- **前向差分法 (Forward Difference)**：
  $$f'(x) \approx \frac{f(x + h) - f(x)}{h}, \quad \text{截斷誤差 } O(h)$$
- **後向差分法 (Backward Difference)**：
  $$f'(x) \approx \frac{f(x) - f(x - h)}{h}, \quad \text{截斷誤差 } O(h)$$

#### 2. 數值積分 (Numerical Quadrature)
計算定積分 $\int_a^b f(x) dx$，步長 $h = \frac{b - a}{n}$：
- **辛普森法 (Simpson's 1/3 Rule, 預設)**：
  $$\int_a^b f(x) dx \approx \frac{h}{3} \left[ f(x_0) + 4 \sum_{i \text{ 奇數}} f(x_i) + 2 \sum_{i \text{ 偶數}} f(x_i) + f(x_n) \right], \quad \text{截斷誤差 } O(h^4)$$
- **梯形法 (Trapezoidal Rule)**：
  $$\int_a^b f(x) dx \approx \frac{h}{2} \left[ f(a) + 2 \sum_{i=1}^{n-1} f(x_i) + f(b) \right], \quad \text{截斷誤差 } O(h^2)$$
- **中點黎曼和 (Midpoint Rule)**：
  $$\int_a^b f(x) dx \approx h \sum_{i=0}^{n-1} f\left(a + (i + 0.5)h\right), \quad \text{截斷誤差 } O(h^2)$$

---

### 題目 2：單變數蒙地卡羅積分
檔案：[`single_variable.py`](single_variable.py) 函式 `monte_carlo_integral_1d`

根據大數法則 (Law of Large Numbers)，連續隨機變數的期望值估計定積分：
$$I = \int_a^b f(x) dx = (b - a) \mathbb{E}_{X \sim U(a, b)}[f(X)] \approx \frac{b - a}{N} \sum_{i=1}^N f(X_i)$$
其中隨機取樣點 $X_i \sim \text{Uniform}(a, b)$。

估計標準誤 (Standard Error, SE)：
$$\text{SE} = \frac{(b - a) \cdot \sigma_f}{\sqrt{N}}$$
根據中心極限定理 (CLT)，其誤差隨採樣數增加以 $O(N^{-1/2})$ 比例收斂。

---

### 題目 3：多變數微分 (梯度) 與超體積數值積分
檔案：[`multivariable.py`](multivariable.py)

#### 1. 數值梯度 (Numerical Gradient)
對於純量場 $f: \mathbb{R}^n \to \mathbb{R}$，梯度向量定義為各方向之偏導數：
$$\nabla f(\mathbf{x}) = \left[ \frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \dots, \frac{\partial f}{\partial x_n} \right]^T$$
函式 `numerical_gradient` 使用中心差分法計算各分量：
$$\frac{\partial f}{\partial x_i} \approx \frac{f(\mathbf{x} + h \mathbf{e}_i) - f(\mathbf{x} - h \mathbf{e}_i)}{2h}$$

#### 2. 超體積數值積分 (Hypervolume Numerical Integration)
對超長方體區域 $\Omega = [low_1, high_1] \times \dots \times [low_n, high_n]$ 進行中點網格切分，微元體積為：
$$dV = \prod_{i=1}^n \Delta x_i = \prod_{i=1}^n \frac{high_i - low_i}{k}$$
積分估計值為各網格中心點之函數值與超體積微元乘積之總和：
$$\int_\Omega f(\mathbf{x}) d\mathbf{x} \approx \sum_{\mathbf{m} \in \text{Midpoints}} f(\mathbf{m}) \cdot dV$$

---

### 題目 4：多變數蒙地卡羅超體積積分
檔案：[`multivariable.py`](multivariable.py) 函式 `monte_carlo_integral_nd`

將超立方體區域 $\Omega$ 總超體積記為 $V = \prod_{i=1}^n (high_i - low_i)$：
$$I = \int_\Omega f(\mathbf{x}) d\mathbf{x} \approx V \cdot \frac{1}{N} \sum_{i=1}^N f(\mathbf{X}_i), \quad \mathbf{X}_i \sim \text{Uniform}(low, high)$$
支援指示函數 (Indicator function)，例如計算任意維度幾何形狀（如 4 維超球體 $V_4 = \frac{\pi^2}{2} R^4$）的超體積。

---

### 題目 5：黎曼積分法函數 `integral(f, low, high)` 與「維度災難」
檔案：[`riemann.py`](riemann.py)

#### 題目規範與定義
撰寫通用介面函式 `integral(f, low, high)`，其中陣列 `low` 與 `high` 之長度即為積分維度 $n$。
測試函數為：
$$f(\mathbf{x}) = \sum_{i=1}^n x_i^2, \quad low = [0, \dots, 0], \quad high = [1, \dots, 1]$$

#### 理論解析解推導
由於積分區域為 $[0, 1]^n$，被積函數各變數相互獨立（可分離）：
$$\int_0^1 \dots \int_0^1 \left(\sum_{i=1}^n x_i^2\right) dx_1 \dots dx_n = \sum_{i=1}^n \left( \int_0^1 x_i^2 dx_i \prod_{j \neq i} \int_0^1 1 dx_j \right) = \sum_{i=1}^n \left(\frac{1}{3} \times 1\right) = \frac{n}{3}$$
- $n = 1$ 時：$\frac{1}{3} \approx 0.333333$
- $n = 2$ 時：$\frac{2}{3} \approx 0.666667$
- $n = 5$ 時：$\frac{5}{3} \approx 1.666667$
- $n = 100$ 時：$\frac{100}{3} \approx 33.333333$

#### 核心發現：維度災難 (Curse of Dimensionality)
黎曼網格法若每個維度切分 $k$ 個區間，總評估點數為 $k^n$：
- $n = 1, k = 1000 \implies 1,000$ 點（約 0.003 秒完成）
- $n = 2, k = 100 \implies 10,000$ 點（約 0.03 秒完成）
- $n = 5, k = 10 \implies 100,000$ 點（約 0.38 秒完成）
- **$n = 100$：即便每軸僅切最粗糙的 $k = 2$ 個格點，總評估點數仍高達：**
  $$2^{100} \approx 1.26765 \times 10^{30} \text{ 個取樣點！}$$
  若以當代超級電腦每秒執行 10 億次 ($10^9$) 浮點計算：
  $$\text{所需時間} \approx \frac{1.26765 \times 10^{30}}{10^9 \times 365.25 \times 86400} \approx 4.02 \times 10^{13} \text{ 年}$$
  **這遠遠超過已知宇宙年齡（約 $1.38 \times 10^{10}$ 年）！**

在 `integral` 函式中，程式會智能檢測點數規模；當偵測到 $n=100$ 網格點數超越物理可能界限時，主動拋出語意明確的 `DimensionalityCurseError` 並詳細輸出理論原因，精準點出確定性數值網格在高維空間下的絕對極限。

---

### 題目 6：蒙地卡羅多變數積分 `mc_integral(f, low, high)` 與高維破局
檔案：[`mc_integral.py`](mc_integral.py)

#### 為什麼蒙地卡羅法能突破高維維度災難？
蒙地卡羅法的誤差收斂階數僅取決於隨機樣本數 $N$：
$$\text{Error} \sim \mathcal{O}\left(\frac{1}{\sqrt{N}}\right)$$
**這個收斂階數完全與維度 $n$ 無關 (Dimension-independent)**！
無論是 1 維還是 100 維，只要抽取 $N = 300,000$ 個點，均能獲得統計標準誤約 $0.005$ 程度的極高精度。

---

## 第 5 題與第 6 題綜合實驗對比

在同一台機器上執行被積函數 $f(\mathbf{x}) = \sum_{i=1}^n x_i^2$ 於 $[0, 1]^n$ 區域的實測數據如下：

| 維度 ($n$) | 理論解析解 ($n/3$) | 黎曼積分估計值 (`integral`) | 蒙地卡羅估計值 (`mc_integral`, $N=300\text{k}$) | 黎曼法耗時 | 蒙地卡羅耗時 | 誤差分析結論 |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1 維** | **0.333333** | 0.333333 | 0.333464 ± 0.000544 | 0.003s | 0.010s | 兩者均極為精準 |
| **2 維** | **0.666667** | 0.666650 | 0.665849 ± 0.000769 | 0.034s | 0.019s | 黎曼網格 $100^2$ 點，蒙地卡羅落於 95% 信心區間 |
| **5 維** | **1.666667** | 1.662500 | 1.666070 ± 0.001217 | 0.381s | 0.039s | 黎曼法耗時呈指數上升，蒙地卡羅表現穩定 |
| **100 維** | **33.333333** | ⚠️ **維度災難 (無法計算)**<br>($2^{100} \approx 1.27\times 10^{30}$ 點) | **33.335055 ± 0.005438** | 無窮大 ($>10^{13}$ 年) | **0.700s** | **蒙地卡羅僅耗時 0.7 秒即完成，絕對誤差僅 0.0017！** |

> **結論**：本實驗完美驗證了數值分析經典結論——**低維空間適用確定性黎曼網格法以取得極致精度；而超高維空間（如 $n=100$）唯有依託蒙地卡羅隨機取樣法方能破解維度災難。**

---

## 專案目錄結構

```text
numerical_methods/
├── README.md              # 完整說明文件 (含 AI 使用聲明與數理分析)
├── __init__.py            # 模組統一匯出入口
├── single_variable.py     # 【題目 1 & 2】單變數數值微積分與蒙地卡羅積分
├── multivariable.py       # 【題目 3 & 4】多變數數值梯度與超體積積分 (數值與蒙地卡羅)
├── riemann.py             # 【題目 5】n 變數黎曼積分 integral(f, low, high)
├── mc_integral.py         # 【題目 6】n 變數蒙地卡羅積分 mc_integral(f, low, high)
├── main.py                # 全題型完整示範與對比測試主程式
└── tests/
    ├── __init__.py
    └── test_numerical.py  # 完整單元測試套件 (unittest, 9 項測試)
```

---

## 快速開始與執行測試

本專案基於 **Python 3.8+** 與 **NumPy** 開發。

### 1. 執行全題目綜合示範
直接執行 [`main.py`](main.py)，將會自動依序執行 1 到 6 題的所有數值範例、對比表格與維度災難分析：

```bash
python main.py
```

### 2. 執行單元測試 (Unit Tests)
專案內建完整的 `unittest` 測試套件，涵蓋所有演算法精度與例外保護：

```bash
python -m unittest discover -s tests -v
```

測試輸出範例：
```text
test_multivariable_gradient ... ok
test_multivariable_hypervolume_integral ... ok
test_multivariable_monte_carlo ... ok
test_question_5_dimensionality_curse ... ok
test_question_5_riemann_integral ... ok
test_question_6_mc_integral ... ok
test_single_variable_differentiation ... ok
test_single_variable_integration ... ok
test_single_variable_monte_carlo ... ok

----------------------------------------------------------------------
Ran 9 tests in 1.491s

OK
```

### 3. 單獨測試各別題目
亦可單獨運行各模組自帶的 `__main__` 測試：

```bash
python single_variable.py   # 題目 1, 2
python multivariable.py     # 題目 3, 4
python riemann.py           # 題目 5 (1, 2, 5, 100 維黎曼測試)
python mc_integral.py       # 題目 6 (1, 2, 5, 100 維蒙地卡羅測試)
```

---

## 程式碼簡化與設計哲學 (Code Simplification)

本專案貫徹以下軟體工程與簡化設計準則：
1. **結構清晰，杜絕過度封裝**：每個模組各司其職，避免無意義的 Abstract Base Class 或過度設計的包裝器。
2. **優先保證行為精確與數學嚴謹**：保留必要的數值保護（如分母為零、維度長度不符、步長負數檢核）。
3. **優雅處置邊界與異常**：當面對 $n=100$ 的維度災難時，透過自訂例外 `DimensionalityCurseError` 清晰回報計算瓶頸，而非讓系統遭遇 MemoryError 或死鎖。
4. **型別提示與文件詳盡**：全函式具備完整 Python Type Hints 與標準數學符號 Docstring。
