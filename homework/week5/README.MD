# 第五週習題

1. 河內塔問題，請分別用遞迴和禁止遞迴兩種方式來解決
2. 請用遞迴解決符號數學式微分的問題，`sym_diff(expr)`
3. 請自製 map, filter, reduce 函數，然後禁止使用迴圈，解決泡沫排序的問題。

參考：https://github.com/ccc115a/alg/tree/main/_more/homework/week5

## 資料夾結構

```
week5/
├── README.MD
├── 01-hanoi/
│   ├── hanoi_rec.py    # 遞迴解
│   └── hanoi_loop.py   # 禁止遞迴解（奇偶循環法）
├── 02-sym_diff/
│   └── sym_diff.py     # 符號微分 + 化簡 + 10 組測試
└── 03-fp/
    └── fp.py           # 自製 my_map/my_filter/my_reduce + 無迴圈泡沫排序
```

## 執行方式

```bash
python 01-hanoi/hanoi_rec.py
python 01-hanoi/hanoi_loop.py
python 02-sym_diff/sym_diff.py
python 03-fp/fp.py
```

## 1. 河內塔 Hanoi

遞迴關係：`H(1)=1, H(n)=2*H(n-1)+1`，共 `2^n - 1` 步。

### 遞迴版 `hanoi_rec.py`

```python
hanoi_recursive(n-1, source, auxiliary, target)  # n-1 個 source -> auxiliary
print(n, source -> target)                       # 第 n 個 source -> target
hanoi_recursive(n-1, auxiliary, target, source)  # n-1 個 auxiliary -> target
```

`n=3, A->C` 輸出 7 步，與理論一致。

### 禁止遞迴版 `hanoi_loop.py`

不用函數自我呼叫，全程只用 `for`：

* 總步數 `2^n - 1`
* 奇數步：只動最小盤 `1`，沿固定循環走
  * `n` 為奇數：`source -> target -> auxiliary -> source ...`
  * `n` 為偶數：`source -> auxiliary -> target -> source ...`
* 偶數步：在「另外兩根」柱子間做唯一合法移動（`move_disk`：空柱必移、小壓大才移）

已驗證 `n=1..4` 兩版移動序列完全相同。

## 2. 符號微分 `sym_diff(expr)`

用 AST（語法樹）+ 遞迴 `diff`：

| 節點 | 微分規則 |
|------|----------|
| `Const(c)` | `0` |
| `Var(x)` | `1`（若 `x==var`）否則 `0` |
| `Add(f,g)` | `f' + g'` |
| `Mul(f,g)` | `f'*g + f*g'`（乘法法則） |
| `Power(f,n)` | `n*f^(n-1)*f'`（次方律+連鎖律） |
| `Sin(f)` | `cos(f)*f'` |
| `Cos(f)` | `-sin(f)*f'` |

`sym_diff(expr, var='x')` 即呼叫 `expr.diff(var)`，全遞迴下降。
`simplify(expr)` 再遞迴化簡 `0/1`（如 `0+x=x`、`1*x=x`、`0*x=0`）。

內建 10 組測試：

1. `5` → `0`
2. `x^3` → `3*x^2`
3. `4*x^2+3*x+7`
4. `sin(x)` → `cos(x)`
5. `cos(3*x)`
6. `sin(x)+cos(x)`
7. `x^2*sin(x)`（乘法法則）
8. `(2*x+5)^4`（連鎖律）
9. `sin(x^2)`
10. `3*x^2+sin(2*x)*cos(x)`

## 3. 自製 FP + 無迴圈泡沫排序

### 自製高階函數（全遞迴，零 `for/while`）

```python
my_map(func, lst)    # [f(head)] + map(f, tail)
my_filter(func, lst) # 滿足則保留 head，否則丟棄，再遞迴 tail
my_reduce(func, lst, init) # fold: reduce(f, tail, f(init, head))
```

### 泡沫排序（禁止迴圈）

* `bubble_pass(acc, cur)`：給 `my_reduce` 用的比較函數，`acc=(processed, max_val)`，大的留下來往後浮。
* `bubble_sort_pass(lst)`：用一次 `my_reduce` 把最大值浮到尾端（= 內層迴圈）。
* `bubble_sort(lst, n)`：遞迴做 `n` 輪，每輪固定尾端一個最大值（= 外層迴圈）。

```python
bubble_sort([64,34,25,12,22,11,90,5])
# [5,11,12,22,25,34,64,90]
```

全程只用遞迴 + `my_reduce`，無任何 `for/while`。
