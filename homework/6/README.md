# Lambda Calculus 解譯器（顯示完整計算過程）

> 習題 6：寫一個 Lambda Calculus 解譯器，要能顯示完整的計算過程。
> 本專案放在桌面 `LambdaCalculusInterpreter/`，純 Python 標準函式庫，無需安裝套件。

## 功能

- **有名稱 / 沒名稱雙顯示**：預設顯示有名稱版本（`\x.x`），加 `--debruijn` 同時顯示 De Bruijn index 版（`(\.(1 0))`，自由變數保留原名）。
- **完整計算過程**：每一步 `[Step i]` + 使用的 `beta:` 規則 + `alpha-conversion` 說明，最後統計步數與是否到達 Normal Form。
- **兩種求值策略**：`--strategy normal`（最左最外，保證找到 normal form）／`applicative`（最左最內，貼近嚴格求值，會展示發散差異）。
- **避免變數捕捉**：capture-avoiding substitution，`06-capture.lc` 可見 α-conversion。
- **Church 解碼**：結果若是 Church numeral / boolean 會自動「解讀為：5 (Church numeral)」等（注意 `FALSE` 與 `0` 是同一個 term，會特別標註）。
- **`.lc` 程式檔 + REPL + `-e`**：三種輸入方式。

## 檔案一覽

```
LambdaCalculusInterpreter/
  lambda_interp.py      # 主程式（lexer / parser / AST / substitution / reduction / De Bruijn / CLI / REPL）
  test_lambda.py        # 單元測試（pytest）
  README.md             # 本檔
  過程文件.md           # AI 協作過程文件（習題要求的「網址或過程文件」）
  run_all.bat           # Windows 一鍵跑完全部範例
  examples/
    prelude.lc          # 共用定義：TRUE/FALSE/IF/AND/OR/NOT/SUCC/ADD/MULT/POW/PRED/SUB/ISZERO/LEQ/EQ/NIL/CONS/CAR/CDR/ISNIL/Y/Z
    01-identity.lc      # 基本 beta：I / K / K*
    02-bool.lc          # Church 布林（需 prelude）
    03-numeral.lc       # Church 數字算術（需 prelude）
    04-omega.lc         # OMEGA 發散（步數上限示範）
    04-strategy.lc      # normal vs applicative 差異（需 prelude）
    05-factorial.lc     # Y combinator 階乘 FACT 2（需 prelude，--max-steps 300）
    06-capture.lc       # 變數捕捉與 alpha-conversion
    07-list.lc          # Church List（需 prelude）
```

## 語法

```
term   ::= app
app    ::= atom { atom }              # 左結合：f x y = ((f x) y)
atom   ::= IDENT | NUMBER | '(' term ')' | abstraction
abstraction ::= ('\' | 'λ' | 'lambda') IDENT+ '.' term   # \x y. body = \x.\y.body
statement   ::= 'let' IDENT '=' term | term               # 一行一個，# 為註解
NUMBER ::= 0 | 1 | 2 | ...            # 語法糖，自動展開成 Church numeral
```

`let` 定義會在求值前以 inline 展開（並顯示「展開定義後」），遞迴定義用 `Y`/`Z` 表達。

## 執行方式（Windows 請先 `chcp 65001` 以正確顯示中文）

```bat
chcp 65001
cd %USERPROFILE%\OneDrive\桌面\LambdaCalculusInterpreter

:: 基本
python lambda_interp.py examples\01-identity.lc
python lambda_interp.py examples\06-capture.lc
python lambda_interp.py examples\04-omega.lc --max-steps 6

:: 需要 prelude 的（布林 / 數字 / 策略 / 階乘 / List）
python lambda_interp.py --prelude examples\prelude.lc examples\02-bool.lc
python lambda_interp.py --prelude examples\prelude.lc examples\03-numeral.lc
python lambda_interp.py --prelude examples\prelude.lc examples\07-list.lc
python lambda_interp.py --prelude examples\prelude.lc examples\05-factorial.lc --max-steps 300

:: 策略對比（同一檔案，normal 1 步成功、applicative 發散）
python lambda_interp.py --prelude examples\prelude.lc --strategy normal examples\04-strategy.lc
python lambda_interp.py --prelude examples\prelude.lc --strategy applicative examples\04-strategy.lc --max-steps 8

:: 沒名稱版（De Bruijn）雙顯示
python lambda_interp.py --debruijn examples\01-identity.lc
python lambda_interp.py --debruijn --prelude examples\prelude.lc examples\02-bool.lc

:: 單行求值 / REPL
python lambda_interp.py -e "(\x.x) y"
python lambda_interp.py --prelude examples\prelude.lc -e "ADD 2 3"
python lambda_interp.py --prelude examples\prelude.lc
```

常用參數：`--strategy normal|applicative`、`--max-steps N`（預設 100，FACT 2 需 300、FACT 3 需 800）、
`--debruijn`、`--unicode`（用 λ 顯示）、`--no-decode`（關閉 Church 解碼）、`--prelude FILE`。

## 範例輸出（節錄）

```
--- Expr 1: (\x.x) y
    展開定義後：(\x.x) y
    [Step 0] (\x.x) y
    [Step 1] y
      => beta: (\x.x) (y)
    [OK] 已到達 Normal Form，共 1 步。(normal)
```

變數捕捉範例會多出一行 alpha 說明：

```
--- Expr 1: (\x y.x y) y
    [Step 0] (\x y.x y) y
    [Step 1] \v1.y v1
      => beta: (\x.\y.x y) (y) [alpha-conversion: \y -> \v1 (avoid capture of y)]
    [OK] 已到達 Normal Form，共 1 步。(normal)
```

## 測試

```bat
python -m pytest test_lambda.py -v
```

共 10 個測試：基本化簡、K、捕捉避免、ADD、MULT、NOT、OMEGA 發散、策略差異、FACT 2、De Bruijn 往返。

## 參考

- 课程參考實作（Python 內嵌 Church encoding，無 parser、无逐步顯示）：
  https://github.com/ccc115a/alg/tree/main/02-%E6%96%B9%E6%B3%95/04c-LambdaCalculus
- 本專案與其差異見 `過程文件.md`。
