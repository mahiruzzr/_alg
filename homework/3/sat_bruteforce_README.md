# SAT 暴力解說明

對應程式：`sat_bruteforce.py`

SAT 問題：給定布林公式，問是否存在一組變數指派使其為真。參考 https://en.wikipedia.org/wiki/Boolean_satisfiability_problem

本程式只處理 CNF（子句的 AND），用真值表暴力列舉求解。

## 輸入表示法

採 DIMACS 風格（不含結尾 0）：

* 變數編號 `1..n`，文字正數表 `x_i`，負數表 `~x_i`
* clause = OR，例如 `[1, -2]` 表 `(x1 OR ~x2)`
* clauses = AND，例如 `[[1, 2], [-1, 2]]` 表 `(x1 OR x2) AND (~x1 OR x2)`

## 方法

二進位計數 `0..2^n-1`，每個整數的二進位對應一組指派（`assignment_from_int`），由 `iter_truth_table` 系統性列舉，保證不重不漏，再逐組用 `eval_cnf` 檢查。

* `solve_sat(n, clauses)`：回第一組解，UNSAT 回 `None`
* `solve_sat_all(n, clauses)`：回全部解
* `solve_sat(..., verbose=True)`：印出完整真值表

複雜度：`O(2^n * m * k)`，n=變數數，m=子句數，k=平均子句長度。

## 執行（Windows）

```powershell
Set-Location -LiteralPath "C:\Users\zhangzhengrong\OneDrive\桌面"
python .\sat_bruteforce.py
```

注意 Windows 用 `python`，不是 `python3`。

## 內建範例

* EX1 `[[1,2],[-1,2]]`：SAT，第一組解 `{x1=F, x2=T}`，共 2 組
* EX2 `[[1],[-1]]`：UNSAT，全部 2 組都不滿足
* EX3 `[[1,-2],[-1,2,3],[-3]]`：SAT，第一組解 `{x1=F, x2=F, x3=F}`，共 2 組

## 限制

暴力法 n 超過約 20 就會太慢（2^n 爆炸），僅適合教學與小規模驗證，大規模請用 DPLL / CDCL 求解器。
