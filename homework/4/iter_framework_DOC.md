# iter_framework.py 說明文件：統一迭代框架與九種經典演算法

> 對應程式：`02-方法/03-迭代法/05-framework/iter_framework.py`（194 行，依賴 `numpy`）
> 補充對照：`iter_nobel_nn.py`（Hopfield + RBM，同樣套用此框架）
> 教材背景：迭代法 `x_{n+1} = g(x_n)`，參考 `01a-equation/iterative3.py`（三種求 sqrt(3) 的改寫比較）

---

## 1. 一句話總覽

本程式把**所有迭代法**抽象成同一句話：

```
state_{n+1} = transition(state_n)，直到 is_converged 成立
```

`generic_iterator()` 只負責「推進 + 判停」的迴圈，九個 `demo_*()` 各自提供不同的 `transition / is_converged / initial_state`，就展示了從國中數學（不動點、牛頓法）到研究所（PageRank、K-Means、EM、QR、RK4、冪次法）的全系列演算法。學會這個框架，就學會了「如何把任何逐步逼近問題裝進同一個模子」。

---

## 2. 核心：generic_iterator()

```python
def generic_iterator(transition_func, is_converged, initial_state, max_iter=1000):
    state = initial_state
    for iteration in range(max_iter):
        next_state = transition_func(state)
        if is_converged(state, next_state, iteration):
            return next_state, iteration + 1
        state = next_state
    print("  [警告] 達到最大迭代次數仍未完全收斂")
    return state, max_iter
```

| 參數 | 型別 | 意義 |
|------|------|------|
| `transition_func` | `state -> next_state` | 狀態推進函數 `g`，即數學上的 `g(x)`。純函數，不要有副作用 |
| `is_converged` | `(old, new, i) -> bool` | 收斂/終止判定。注意它拿到的是舊新兩個狀態 + 當前輪數，所以既可寫「誤差型」也可寫「步數型」 |
| `initial_state` | 任意 | 初值。可以是純量 `float`、向量 `ndarray`、矩陣 `ndarray`、甚至 `tuple(t,y)`、`tuple(centroids)`、`tuple(theta)` |
| `max_iter` | int，預設 1000 | 安全上限，避免無窮迴圈 |
| 回傳 | `(final_state, iters)` | 最終狀態 + 實際用掉的次數（注意是 `iteration+1`，從 1 起算） |

設計要點：

1. **分離關注點**：`transition` 只管「下一步怎麼走」，`is_converged` 只管「何時停」，主迴圈完全通用。
2. **狀態泛型**：框架不假設 `state` 是數字。只要 `transition` 吃什麼吐什麼、`is_converged` 會比，就能用。這是本程式能同時裝下純量、向量、矩陣、`(t,y)` 元組的原因。
3. **兩種判停模式**：大部分 demo 用「誤差型」（如 `norm(new-old)<1e-6`），RK4 和後面的 RBM 用「步數/目標型」（如 `t>=t_end`、`i>=k-1`）。這揭示了迭代法的廣義定義：不一定是收斂到不動點，走固定步數也算迭代。
4. **失敗語義**：超時不丟例外，而是印警告並回傳當前狀態 + `max_iter`，呼叫端可據此判斷是否收斂。

虛擬流程：

```
state <- initial
for i in 0..max_iter-1:
    next <- g(state)
    if converged(state, next, i): return next, i+1
    state <- next
warn; return state, max_iter
```

---

## 3. 九個 Demo 一覽

| # | 函數 | 數學問題 | state 型別 | transition 本質 | converged 本質 | 收斂速度/步數參考 |
|---|------|----------|------------|-----------------|----------------|-------------------|
| 1 | `demo_fixed_point` | 2D 線性不動點 `X=AX+b` | `(2,)向量` | 仿射映射 | `norm差<1e-6` | 線性，約十餘步 |
| 2 | `demo_newton` | `x^2-4=0` 求根 | 純量 | 牛頓 `x-f/f'` | `abs差<1e-6` | 二階，約 5 步（初值 1.0→2.0） |
| 3 | `demo_gauss_seidel` | `Ax=b` (3x3) | `(3,)向量` | 逐分量就地更新 | `max abs差<1e-6` | 線性，十餘步 |
| 4 | `demo_power_iteration` | 主特徵對 `(lambda,v)` | `(3,)單位向量` | `Av/‖Av‖` | `allclose(old,new)` | 線性，速率比 `|l2/l1|` 決定 |
| 5 | `demo_qr_algorithm` | 全部特徵值 | `(3,3)矩陣` | `Ak -> RQ` | 非對角元和 `<1e-6` | 線性/二次之間 |
| 6 | `demo_rk4` | ODE `dy/dt=y-t+1, y(0)=1` 到 `t=2` | `tuple(t,y)` | RK4 單步 `h=0.2` | `t>=t_end` | 非收斂型，固定 10 步 |
| 7 | `demo_pagerank` | `r=G r` 穩態分佈 | `(4,)機率向量` | `Gr` | `norm差<1e-6` | 線性，速率由 damping `d=0.85` 決定 |
| 8 | `demo_kmeans` | 2 群分群 (30 點) | `(2,2)中心矩陣` | E-step+ M-step | `max abs差<1e-6` | 有限步穩定（Hard EM） |
| 9 | `demo_em_two_coin` | 兩枚硬幣 `theta_A,B` 估計 | `tuple(2)` | E-step 加權 + M-step 更新 | 雙參數差 `<1e-6` | 線性，初值敏感 |

以下逐一詳解。

### 3.1 demo_fixed_point — 二維不動點迭代

```python
transition = lambda X: [0.5*X0-0.2*X1+0.3, 0.2*X0+0.5*X1+0.4]
```

* 數學：解 `X = M X + c`，其中 `M=[[0.5,-0.2],[0.2,0.5]]`。若 `M` 譜半徑 `<1` 則對任意初值收斂到唯一不動點。此例初值 `[0,0]`。
* 為何收斂：`M` 特徵值 `0.5±0.2i`，模約 `0.538<1`，為壓縮映射（Banach 不動點定理保證）。
* 教學意義：最純粹的 `x=g(x)` 範例，對應教材 `iterative3.py` 的精神：改寫形式決定成敗。

### 3.2 demo_newton — 牛頓法求根

```python
f=x^2-4; df=2x; transition = x - f/df
```

* 數學：牛頓迭代 `x_{n+1}=x-f(x)/f'(x)`，幾何意義是「用切線零點代替曲線零點」。
* 初值 `1.0` 求正根 `2.0`，誤差平方級縮小（`g'(alpha)=0`，二階收斂），通常 5–6 步達 `1e-6`。
* 對比教材 `f3=(x+3/x)/2`：那正是 `f(x)=x^2-3` 的牛頓式，本 demo 只是把 3 換成 4。
* 注意：若初值取 `0` 會除零；取負值會收斂到 `-2`。說明牛頓法是**局部**收斂。

### 3.3 demo_gauss_seidel — 高斯-賽得爾解線性方程

```python
A=[[4,-1,0],[-1,4,-1],[0,-1,4]]; b=[7,2,13]
for i: x_new[i]=(b[i]-sum_{j!=i} A[i,j]*x_new[j])/A[i,i]
```

* 數學：把 `Ax=b` 拆成逐行解，用**最新**分量就地覆蓋（與 Jacobi 用舊向量一次更新不同，故收斂較快）。
* `converged` 用無窮範數 `max|diff|<1e-6`，適合向量。
* 此 `A` 為嚴格對角優勢 + 對稱正定，理論保證收斂。真解可手算驗證。
* 框架視角：`state` 是向量，`transition` 內部含迴圈，但對框架而言仍是「一步」。

### 3.4 demo_power_iteration — 冪次法求主特徵向量

```python
transition = A v / ‖A v‖
```

* 數學：反覆乘 `A` 並歸一化，`v` 會被放大最多的主特徵方向主導。`eigenval = v^T A v`（Rayleigh 商）即主特徵值。
* 初值用 `seed(42)` 隨機單位向量，避免恰與主方向正交的極端情形。
* `converged = allclose(old,new)`：注意特徵向量有正負號不定性，此例 `A` 正定、初值正，符號穩定；一般實作需用 `allclose(old,new) or allclose(old,-new)` 或看 Rayleigh 商差。
* 與 SVD/PCA/PageRank 的關係：三者底層都是冪次法。

### 3.5 demo_qr_algorithm — QR 求全部特徵值

```python
transition = lambda Ak: RQ  where Q,R = qr(Ak)   # 程式寫成 dot(*reversed(qr(Ak)))
converged = sum|非對角元| < 1e-6
```

* 數學：`Ak = Qk Rk → A_{k+1}=Rk Qk`，相似變換下特徵值不變，`Ak` 漸趨上三角，對角線即特徵值。本例 `A` 對稱，故趨向對角陣。
* 程式技巧：`np.linalg.qr` 回傳 `(Q,R)`，`reversed` 後 `dot(R,Q)` 即一步 QR 迭代，一行寫完。
* 判停用「非對角能量」`sum| A-diag(diag(A)) |`，是實務常用準則。
* 教學點：`state` 是矩陣，證明框架與維度無關。

### 3.6 demo_rk4 — 四階龍格-庫塔解 ODE

```python
f(t,y)=y-t+1; h=0.2; t_end=2.0
k1=f(t,y); k2=f(t+h/2,y+h*k1/2); k3=...; k4=...; return (t+h, y+h*(k1+2k2+2k3+k4)/6)
converged = new_t >= t_end
```

* 數學：解 `dy/dt=y-t+1, y(0)=1`，解析解 `y=t+e^t`，`y(2)≈9.389`，可對照驗證。`h=0.2` 共 10 步。
* 框架視角的特殊性：這裡 `is_converged` **不是誤差**，而是「時間到沒」。說明框架的 `is_converged` 實為廣義「終止條件」。回傳的 `iters` 在此應讀作「步數」而非「收斂步數」。
* `state=(t,y)` 元組展示了框架可攜帶多 field 狀態。

### 3.7 demo_pagerank — PageRank 穩態分佈

```python
M = 4x4 跳轉矩陣; G = d*M + (1-d)/n*1 (d=0.85); transition = G r
```

* 數學：隨機衝浪者模型，求 `G` 的主特徵向量（`PageRank` 即冪次法的應用）。`damping 0.85` 保證 `G` 為正隨機矩陣（Perron 定理保證唯一穩態）。
* 初值均勻 `[0.25]*4`，`converged` 用 `norm差`。
* 與 demo 4 的關係：本質同為冪次法，只是矩陣有機率歸一結構，結果可解釋為「網頁重要性」。

### 3.8 demo_kmeans — K-Means（Hard EM）

```python
def transition(centroids):
    labels = argmin‖X-centroids‖  # E-step
    return mean(X[labels==j])     # M-step
```

* 資料：30 點，兩團高斯 `(2,2)`、`(-2,-2)`，`seed(42)` 可重現。初值取前兩筆 `X[:2]`。
* 數學：交替「分配—更新」，目標函數（組內平方和）單調遞減，有限步穩定，但只保證局部最優，初值敏感。
* 潛在坑：若某群無點，`mean([])` 會 `nan`。本資料團分明不會觸發，實務需處理空群。
* 框架視角：`transition` 內含兩步（E+M），但對外仍是一步映射，完美示範「複合推進也可裝進框架」。

### 3.9 demo_em_two_coin — EM 估計雙硬幣

* 經典例子（5 組各 10 次實驗：`[[5,5],[9,1],[8,2],[4,6],[7,3]]`），未知每次用的是 A 還是 B 幣，估 `theta_A, theta_B`。
* `transition(theta)`：
  * E-step：依當前 `theta` 算每組來自 A 的後驗 `p_A = L_A/(L_A+L_B)`；
  * M-step：加權計數更新 `theta_A = 期望正面_A/期望總數_A`。
* 初值 `(0.6,0.5)`，判停雙參數差 `<1e-6`，結果約 `(0.80,0.52)`（與統計教材一致）。
* 教學點：含潛變數（哪枚幣）時不能直接 MLE，EM 用「期望補齊 + 極大化」迭代逼近。與 K-Means 對比：K-Means 是 Hard 分配（0/1），EM 是 Soft 加權。

---

## 4. 統一模式：三行寫出一個新迭代法

任何新問題只要回答三個問題就能套用框架：

```python
transition = lambda state: ...   # 下一步
converged  = lambda o,n,i: ...   # 何時停
result, iters = generic_iterator(transition, converged, initial_state)
```

以習題 1（求 `cbrt(2)`，`x^3=2`）為例，三種寫法對應三種收斂性：

```python
g1 = lambda x: 2/(x*x)            # |g'|=2>1 發散
g2 = lambda x: x-0.1*(x**3-2)     # |g'|~0.52 線性收斂
g3 = lambda x: (2*x+2/(x*x))/3    # 牛頓，g'=0 二階收斂
generic_iterator(g3, lambda o,n,i: abs(n-o)<1e-10, 1.0)
```

這正是 `iterative3.py`（`f1=3/x` 發散震盪、`f2` 線性、`f3` 牛頓最快）的翻版，證明「改寫方式決定收斂」。

---

## 5. 與諾貝爾獎補充（iter_nobel_nn.py）的關係

`iter_nobel_nn.py` 複用**同一個** `generic_iterator`，只換 `transition/converged`：

* **Hopfield 聯想記憶**：`state` 是 `±1` 向量，`transition = sign(W s)`（Hebbian 權重 `W`，對角歸零），`converged = array_equal(old,new)`（不動點即記憶）。破損圖案經幾步回到記憶，能量單調下降。確定性不動點迭代。
* **RBM CD-k**：`state=(v,h)`，`transition` 是一步 Gibbs 採樣 `v→h→v'`，`converged = i>=k-1`（固定 `k=5` 步，非誤差型，同 RK4 邏輯）。隨機性 MCMC 迭代。

結論：從牛頓法到 Hopfield/RBM，數學外衣不同，骨架都是「推進 + 判停」。這就是本框架的最大教學價值。

---

## 6. 實作注意事項與限制

1. `print("[警告]...")` 只在超時出現，看到它表示發散或 `max_iter` 太小，先檢查 `|g'|` 與初值。
2. `demo_power_iteration` 的 `allclose` 未處理符號翻轉；若換矩陣/初值導致 `v↔-v` 震盪，應改為比較 Rayleigh 商或 `min(‖o-n‖,‖o+n‖)`。
3. `demo_qr` 的判停對非對稱矩陣可能慢或需位移（shift）；本例對稱故簡潔。
4. `demo_kmeans` 取 `X[:2]` 作初值有偶然性；空群會 `nan`，實務應重選中心。
5. `demo_em` 初值敏感，不同初值可能收斂到不同局部極大（label switching）。
6. `demo_rk4` 的 `iters` 是步數（10），勿與「收斂步數」混談；精度由 `h` 決定，減半 `h` 誤差約減為 1/16（四階）。
7. 所有 `transition` 應保持純函數（本程式 `gauss_seidel` 內用 `copy()` 正是為此）。

---

## 7. 如何執行

```bash
pip install numpy
python iter_framework.py
```

輸出九段 `結果: ... (耗時 N 次迭代)`，直接對照第 3 節表格驗證。隨機部分已 `seed(42)`，可重現。

---

## 8. 術語速查

* 不動點 `fixed point`：`x=g(x)` 的解，迭代的目標。
* 壓縮映射：`|g'|(<1)` 保證存在唯一不動點且全局/局部收斂。
* 收斂階：線性（誤差等比縮小，如 g2、PageRank）、二階（誤差平方縮小，如牛頓）、有限步穩定（如 K-Means）。
* Gibbs 採樣 / CD-k：RBM 用短鏈 MCMC 近似梯度，Hinton 2024 Nobel 物理獎工作之一。
* Hebbian / Hopfield 能量：`E=-1/2 s^T W s`，非同步更新下單調降，Hopfield 2024 Nobel 物理獎工作。

---

*本文件對應習題 2：讀懂教材後為 `iter_framework.py` 所寫之說明。習題 1 另見 `iterative_custom_cbrt2.py`（求 cbrt(2) 的三式對比，與 `iterative3.py` 呼應）。*
