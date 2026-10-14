#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lambda Calculus 解譯器 (具完整計算過程顯示)
================================================
* 支援「有名稱」(named) 與「沒名稱」(De Bruijn index) 兩種顯示
* 支援 Normal-order (leftmost-outermost) 與 Applicative-order (leftmost-innermost)
* 顯示每一步 β-reduction (含 α-conversion 說明)，避免變數捕捉 (capture-avoiding substitution)
* 可讀取 .lc 程式檔 (多個範例見 examples/)，也可 -e 直接求值或進入 REPL
* 純標準函式庫，Windows / Linux 皆可跑： python lambda_interp.py examples/02-bool.lc

語法 (examples/prelude.lc 為準):
    term      ::= app
    app       ::= atom { atom }            # 左結合，f x y = ((f x) y)
    atom      ::= IDENT | NUMBER | '(' term ')' | abstraction
    abstraction ::= ('\\' | 'λ' | 'lambda') IDENT+ '.' term
    statement ::= 'let' IDENT '=' term | term     # 一行一個 statement，# 開頭為註解
    NUMBER    ::= 0 | 1 | 2 | ...           # 語法糖，自動展開成 Church numeral

範例:
    let TRUE = \\x.\\y.x
    let FALSE = \\x.\\y.y
    (\\x.x) y
"""

import argparse
import sys

# Windows 舊主控台預設為 cp950，直接 print 中文會亂碼或報錯；
# 這裡盡量把 stdout 切到 utf-8（現代 Windows Terminal / VS Code 內建終端機皆支援）。
# 若仍使用舊 cmd.exe，請先執行 chcp 65001 再跑本程式。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------- AST (有名稱版)

class Var:
    __slots__ = ("name",)
    def __init__(self, name): self.name = name
    def __eq__(self, o): return isinstance(o, Var) and self.name == o.name
    def __hash__(self): return hash(("v", self.name))

class Abs:
    __slots__ = ("param", "body")
    def __init__(self, param, body): self.param = param; self.body = body
    def __eq__(self, o): return isinstance(o, Abs) and self.param == o.param and self.body == o.body
    def __hash__(self): return hash(("a", self.param, self.body))

class App:
    __slots__ = ("func", "arg")
    def __init__(self, func, arg): self.func = func; self.arg = arg
    def __eq__(self, o): return isinstance(o, App) and self.func == o.func and self.arg == o.arg
    def __hash__(self): return hash(("p", self.func, self.arg))

# ------------------------------------------------------- AST (沒名稱 De Bruijn 版)

class DbVar:
    __slots__ = ("index",)
    def __init__(self, index): self.index = index

class DbFree:
    """De Bruijn 顯示中的自由變數（保留原名，教學用）"""
    __slots__ = ("name",)
    def __init__(self, name): self.name = name

class DbAbs:
    __slots__ = ("body",)
    def __init__(self, body): self.body = body

class DbApp:
    __slots__ = ("func", "arg")
    def __init__(self, func, arg): self.func = func; self.arg = arg

# ---------------------------------------------------------------- Lexer

class Tok:
    def __init__(self, kind, text=""):
        self.kind = kind  # LAMBDA DOT LPAREN RPAREN IDENT NUMBER LET EQ NEWLINE SEMI EOF
        self.text = text
    def __repr__(self): return f"Tok({self.kind},{self.text!r})"

def tokenize(src):
    toks = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in " \t\r":
            i += 1; continue
        if c == "\n":
            toks.append(Tok("NEWLINE")); i += 1; continue
        if c == ";":
            toks.append(Tok("SEMI")); i += 1; continue
        if c == "#":
            while i < n and src[i] != "\n": i += 1
            continue
        if c == "\\" or c == "λ" or c == "lambda"[0] and src.startswith("lambda", i) and (i + 6 >= n or not (src[i+6].isalnum() or src[i+6] == "_")):
            if src.startswith("lambda", i) and (c == "l"):
                # 確認是關鍵字 lambda 而非識別字首
                toks.append(Tok("LAMBDA")); i += 6; continue
            if c == "\\" or c == "λ":
                toks.append(Tok("LAMBDA")); i += 1; continue
        if c == ".":
            toks.append(Tok("DOT")); i += 1; continue
        if c == "(":
            toks.append(Tok("LPAREN")); i += 1; continue
        if c == ")":
            toks.append(Tok("RPAREN")); i += 1; continue
        if c == "=":
            toks.append(Tok("EQ")); i += 1; continue
        if c.isdigit():
            j = i
            while j < n and src[j].isdigit(): j += 1
            toks.append(Tok("NUMBER", src[i:j])); i = j; continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] in "_'!?+-*/<>="): j += 1
            word = src[i:j]
            if word == "lambda":
                toks.append(Tok("LAMBDA"))
            elif word == "let":
                toks.append(Tok("LET"))
            else:
                toks.append(Tok("IDENT", word))
            i = j; continue
        raise SyntaxError(f"無法辨識的字元 {c!r} (位置 {i})，整段: {src[max(0,i-20):i+20]!r}")
    toks.append(Tok("EOF"))
    return toks

# ---------------------------------------------------------------- Parser

def church_numeral(n):
    """把 Python 整數轉成 Church numeral AST: λf.λx.f^n(x)"""
    from functools import reduce
    f, x = Var("f"), Var("x")
    body = x
    for _ in range(n):
        body = App(f, body)
    return Abs("f", Abs("x", body))

class Parser:
    def __init__(self, toks):
        self.toks = toks; self.pos = 0

    def peek(self): return self.toks[self.pos]
    def next(self):
        t = self.toks[self.pos]; self.pos += 1; return t
    def expect(self, kind):
        t = self.next()
        if t.kind != kind:
            raise SyntaxError(f"語法錯誤：期望 {kind}，得到 {t}")
        return t

    def parse_program(self):
        """回傳 [(kind, ...)]，kind 為 'let' 或 'expr'"""
        stmts = []
        while True:
            # 跳過空行
            while self.peek().kind in ("NEWLINE", "SEMI"):
                self.next()
            if self.peek().kind == "EOF":
                break
            if self.peek().kind == "LET":
                self.next()
                name = self.expect("IDENT").text
                self.expect("EQ")
                t = self.parse_term()
                stmts.append(("let", name, t))
            else:
                t = self.parse_term()
                stmts.append(("expr", t))
            # statement 結束：容許換行/分號/EOF/RPAREN? 頂層只接受換行分隔
            if self.peek().kind in ("NEWLINE", "SEMI"):
                self.next()
            elif self.peek().kind == "EOF":
                break
            else:
                raise SyntaxError(f"語法錯誤：一個 statement 結束後應換行，得到 {self.peek()}。若想連寫請用括號。")
        return stmts

    def parse_term(self):
        return self.parse_app()

    def parse_app(self):
        atoms = []
        a = self.parse_atom()
        if a is None:
            raise SyntaxError(f"語法錯誤：期望一個 term，得到 {self.peek()}")
        atoms.append(a)
        while True:
            a = self.parse_atom()
            if a is None:
                break
            atoms.append(a)
        t = atoms[0]
        for a in atoms[1:]:
            t = App(t, a)
        return t

    def parse_atom(self):
        t = self.peek()
        if t.kind == "IDENT":
            self.next(); return Var(t.text)
        if t.kind == "NUMBER":
            self.next(); return church_numeral(int(t.text))
        if t.kind == "LPAREN":
            self.next()
            # 括號內可含換行
            saved = self.skip_breaks_inside()
            inner = self.parse_term()
            saved2 = self.skip_breaks_inside()
            self.expect("RPAREN")
            return inner
        if t.kind == "LAMBDA":
            return self.parse_abs()
        return None

    def skip_breaks_inside(self):
        while self.peek().kind in ("NEWLINE", "SEMI"):
            self.next()

    def parse_abs(self):
        self.expect("LAMBDA")
        params = []
        while self.peek().kind == "IDENT":
            params.append(self.next().text)
        if not params:
            raise SyntaxError(f"語法錯誤：λ 後面至少要有一個變數，得到 {self.peek()}")
        self.expect("DOT")
        body = self.parse_term()
        t = body
        for p in reversed(params):
            t = Abs(p, t)
        return t

def parse_program(src):
    return Parser(tokenize(src)).parse_program()

def parse_term(src):
    toks = tokenize(src)
    p = Parser(toks)
    t = p.parse_term()
    return t

# ---------------------------------------------------------------- 基本運算：自由變數 / pretty print

def free_vars(t):
    if isinstance(t, Var): return {t.name}
    if isinstance(t, App): return free_vars(t.func) | free_vars(t.arg)
    if isinstance(t, Abs): return free_vars(t.body) - {t.param}
    raise TypeError(t)

_counter = [0]
def fresh_var(avoid):
    base = "v"
    while True:
        _counter[0] += 1
        for cand in (f"{base}{_counter[0]}", f"x{_counter[0]}", f"y{_counter[0]}", f"z{_counter[0]}"):
            if cand not in avoid:
                return cand

def reset_fresh():
    _counter[0] = 0

def to_string(t, unicode=False, _prec=0):
    """named 版 pretty print，盡量少括號。_prec: 0 頂層, 1 函數位, 2 引數位"""
    lam = "λ" if unicode else "\\"
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Abs):
        # 蒐集連續 λ: \x y. body
        params = [t.param]; body = t.body
        while isinstance(body, Abs):
            params.append(body.param); body = body.body
        s = f"{lam}{' '.join(params)}.{to_string(body, unicode, 0)}"
        return f"({s})" if _prec > 0 else s
    if isinstance(t, App):
        f = to_string(t.func, unicode, 1)
        a = to_string(t.arg, unicode, 2)
        s = f"{f} {a}"
        return f"({s})" if _prec == 2 else s
    raise TypeError(t)

def db_to_string(t):
    if isinstance(t, DbVar): return str(t.index)
    if isinstance(t, DbFree): return t.name
    if isinstance(t, DbAbs): return f"(\\.{db_to_string(t.body)})"
    if isinstance(t, DbApp): return f"({db_to_string(t.func)} {db_to_string(t.arg)})"
    raise TypeError(t)

# ---------------------------------------------------------------- 代換 (capture-avoiding) + α-conversion

def rename(t, old, new):
    """無條件把 bound/unbound 的 old 改名 new（僅內部使用，呼叫前已保證 fresh)。"""
    if isinstance(t, Var):
        return Var(new) if t.name == old else t
    if isinstance(t, App):
        return App(rename(t.func, old, new), rename(t.arg, old, new))
    if isinstance(t, Abs):
        if t.param == old:
            return Abs(new, rename(t.body, old, new))
        return Abs(t.param, rename(t.body, old, new))
    raise TypeError(t)

def subst(t, x, s, alpha_log=None):
    """回傳 t[x := s]，capture-avoiding；若發生 α 轉換，會把說明 append 到 alpha_log。"""
    if isinstance(t, Var):
        return s if t.name == x else t
    if isinstance(t, App):
        return App(subst(t.func, x, s, alpha_log), subst(t.arg, x, s, alpha_log))
    if isinstance(t, Abs):
        y = t.param
        if y == x:
            return t  # x 被遮蔽
        fv_s = free_vars(s)
        if y not in fv_s:
            return Abs(y, subst(t.body, x, s, alpha_log))
        # 會捕捉 → α-conversion
        avoid = free_vars(t.body) | fv_s | {x}
        z = fresh_var(avoid)
        if alpha_log is not None:
            alpha_log.append(f"alpha-conversion: \\{y} -> \\{z} (avoid capture of {y})")
        return Abs(z, subst(rename(t.body, y, z), x, s, alpha_log))
    raise TypeError(t)

def alpha_equal(a, b, env_a=None, env_b=None):
    """檢查 α-equivalence（換 bound 名仍相等）。"""
    env_a = {} if env_a is None else env_a
    env_b = {} if env_b is None else env_b
    if isinstance(a, Var) and isinstance(b, Var):
        da = env_a.get(a.name); db = env_b.get(b.name)
        if da is None and db is None:
            return a.name == b.name
        return da is not None and da == db
    if isinstance(a, Abs) and isinstance(b, Abs):
        n = len(env_a)
        env_a2 = dict(env_a); env_a2[a.param] = n
        env_b2 = dict(env_b); env_b2[b.param] = n
        return alpha_equal(a.body, b.body, env_a2, env_b2)
    if isinstance(a, App) and isinstance(b, App):
        return alpha_equal(a.func, b.func, env_a, env_b) and alpha_equal(a.arg, b.arg, env_a, env_b)
    return False

# ---------------------------------------------------------------- β-reduction (單步)

def has_redex(t):
    if isinstance(t, App) and isinstance(t.func, Abs):
        return True
    if isinstance(t, App):
        return has_redex(t.func) or has_redex(t.arg)
    if isinstance(t, Abs):
        return has_redex(t.body)
    return False

def step_normal(t):
    """Normal order：leftmost-outermost。回傳 (new_term, 說明) 或 None (已是 normal form)。"""
    if isinstance(t, App) and isinstance(t.func, Abs):
        logs = []
        nt = subst(t.func.body, t.func.param, t.arg, logs)
        info = f"beta: (\\{t.func.param}.{to_string(t.func.body)}) ({to_string(t.arg)})"
        if logs:
            info += " [" + "; ".join(logs) + "]"
        return nt, info
    if isinstance(t, App):
        r = step_normal(t.func)
        if r is not None:
            nt, info = r
            return App(nt, t.arg), info
        r = step_normal(t.arg)
        if r is not None:
            nt, info = r
            return App(t.func, nt), info
        return None
    if isinstance(t, Abs):
        r = step_normal(t.body)
        if r is not None:
            nt, info = r
            return Abs(t.param, nt), info
        return None
    return None  # Var

def step_applicative(t):
    """Applicative order：leftmost-innermost（先化簡子項，子項都 normal 才收縮最外層)。"""
    if isinstance(t, App):
        r = step_applicative(t.func)
        if r is not None:
            nt, info = r
            return App(nt, t.arg), info
        r = step_applicative(t.arg)
        if r is not None:
            nt, info = r
            return App(t.func, nt), info
        if isinstance(t.func, Abs):
            logs = []
            nt = subst(t.func.body, t.func.param, t.arg, logs)
            info = f"beta: (\\{t.func.param}.{to_string(t.func.body)}) ({to_string(t.arg)})"
            if logs:
                info += " [" + "; ".join(logs) + "]"
            return nt, info
        return None
    if isinstance(t, Abs):
        r = step_applicative(t.body)
        if r is not None:
            nt, info = r
            return Abs(t.param, nt), info
        return None
    return None

def evaluate_trace(term, strategy="normal", max_steps=100):
    """回傳 (steps, infos, status)。steps[0] 為初始，status ∈ normal/limit。"""
    reset_fresh()
    steps = [term]; infos = [""]
    step_fn = step_normal if strategy == "normal" else step_applicative
    for _ in range(max_steps):
        r = step_fn(steps[-1])
        if r is None:
            return steps, infos, "normal"
        nt, info = r
        steps.append(nt); infos.append(info)
    return steps, infos, "limit"

# ---------------------------------------------------------------- De Bruijn 轉換 (沒名稱版)

def to_debruijn(t, ctx=()):
    if isinstance(t, Var):
        if t.name in ctx:
            # ctx 最內層在最後，index = 反向位置
            return DbVar(list(reversed(ctx)).index(t.name))
        else:
            # 自由變數保留原名（教學顯示用；純理論中 closed term 才有純 index）
            return DbFree(t.name)
    if isinstance(t, Abs):
        return DbAbs(to_debruijn(t.body, ctx + (t.param,)))
    if isinstance(t, App):
        return DbApp(to_debruijn(t.func, ctx), to_debruijn(t.arg, ctx))
    raise TypeError(t)

def from_debruijn(db, ctx=()):
    if isinstance(db, DbVar):
        return Var(ctx[len(ctx) - 1 - db.index])
    if isinstance(db, DbFree):
        return Var(db.name)
    if isinstance(db, DbAbs):
        avoid = set(ctx)
        # 產生不衝突的新名
        base = "x"
        k = len(ctx)
        name = f"{base}{k}" if f"{base}{k}" not in avoid else fresh_var(avoid)
        return Abs(name, from_debruijn(db.body, ctx + (name,)))
    if isinstance(db, DbApp):
        return App(from_debruijn(db.func, ctx), from_debruijn(db.arg, ctx))
    raise TypeError(db)

def try_debruijn_str(t):
    try:
        return db_to_string(to_debruijn(t))
    except ValueError as e:
        return f"<含自由變數，省略: {e}>"

# ---------------------------------------------------------------- Church 解碼 (把結果翻回人類數字/布林)

def decode_church_numeral(t):
    """若 t α-equal 於 λf.λx.f^n(x) 則回傳 n，否則 None。"""
    if not (isinstance(t, Abs) and isinstance(t.body, Abs)):
        return None
    f = t.param; x = t.body.param; body = t.body.body
    n = 0
    while isinstance(body, App) and isinstance(body.func, Var) and body.func.name == f:
        body = body.arg; n += 1
        if n > 10000:
            return None
    if isinstance(body, Var) and body.name == x:
        return n
    return None

def decode_church_bool(t):
    if isinstance(t, Abs) and isinstance(t.body, Abs):
        a, b, body = t.param, t.body.param, t.body.body
        if isinstance(body, Var):
            if body.name == a: return True
            if body.name == b: return False
    return None

def decode_result(t):
    # 注意：Church 0 與 FALSE 是同一個 term（都是 \a.\b.b），先判斷布林 FALSE/TRUE 較符合直覺；
    # 這裡特別標註雙重身分，避免誤會。
    b = decode_church_bool(t)
    n = decode_church_numeral(t)
    if b is True:
        return "TRUE (Church boolean)"
    if b is False:
        return "FALSE (Church boolean，同時也是 Church numeral 0)"
    if n is not None:
        return f"{n} (Church numeral)"
    return None

# ---------------------------------------------------------------- 環境 (let) 展開

def inline_env(t, env, _depth=0):
    """把 t 中引用 env 的自由變數展開成定義（遞迴，防循環，最多 50 層)。"""
    if _depth > 50:
        raise RecursionError("let 定義可能循環參照（展開超過 50 層）")
    if isinstance(t, Var):
        if t.name in env:
            return inline_env(env[t.name], env, _depth + 1)
        return t
    if isinstance(t, App):
        return App(inline_env(t.func, env, _depth), inline_env(t.arg, env, _depth))
    if isinstance(t, Abs):
        # 若 param 遮蔽了 env 中的名字，body 內不展開該名
        if t.param in env:
            inner = {k: v for k, v in env.items() if k != t.param}
            return Abs(t.param, inline_env(t.body, inner, _depth))
        return Abs(t.param, inline_env(t.body, env, _depth))
    raise TypeError(t)

# ---------------------------------------------------------------- 顯示完整過程

def print_trace(term, strategy="normal", max_steps=100, show_debruijn=False,
                unicode=False, decode=True, prefix="", out=None):
    out = sys.stdout if out is None else out
    steps, infos, status = evaluate_trace(term, strategy, max_steps)
    for i, s in enumerate(steps):
        named = to_string(s, unicode)
        line = f"{prefix}[Step {i}] {named}"
        if show_debruijn:
            line += f"\n{prefix}  DeBruijn: {try_debruijn_str(s)}"
        if i > 0 and infos[i]:
            line += f"\n{prefix}  => {infos[i]}"
        print(line, file=out)
    if status == "normal":
        print(f"{prefix}[OK] 已到達 Normal Form，共 {len(steps)-1} 步。({strategy})", file=out)
    else:
        print(f"{prefix}... 達到步數上限 {max_steps}，可能發散 (diverge) 或需更大步數。({strategy})", file=out)
    if decode and status == "normal":
        d = decode_result(steps[-1])
        if d is not None:
            print(f"{prefix}  解讀為：{d}", file=out)
    print(file=out)
    return steps, status

def run_program(src, strategy="normal", max_steps=100, show_debruijn=False,
                unicode=False, decode=True):
    """執行一整份 .lc 原始碼：依序處理 let / expr，每個 expr 印出完整過程。"""
    reset_fresh()
    stmts = parse_program(src)
    env = {}
    n_expr = 0
    for st in stmts:
        if st[0] == "let":
            _, name, t = st
            env[name] = t
            print(f"let {name} = {to_string(t, unicode)}")
            if show_debruijn:
                print(f"  DeBruijn: {try_debruijn_str(inline_env(t, env))}")
        else:
            _, t = st
            n_expr += 1
            full = inline_env(t, env)
            print(f"--- Expr {n_expr}: {to_string(t, unicode)}")
            print(f"    展開定義後：{to_string(full, unicode)}")
            print_trace(full, strategy, max_steps, show_debruijn, unicode, decode, prefix="    ")
    if n_expr == 0:
        print("(此檔案只有定義，沒有待求值的式子)")

# ---------------------------------------------------------------- CLI / REPL

def repl(strategy, max_steps, show_debruijn, unicode, decode):
    print("Lambda Calculus REPL — 輸入 term 或 let NAME = term，空行求值，:quit 離開")
    print("  例：let TRUE = \\x.\\y.x")
    print("  例：(\\x.x) y     例：:strategy applicative   例：:debruijn on")
    env = {}
    buf = ""
    while True:
        try:
            line = input("lc> " if not buf else "..> ")
        except (EOFError, KeyboardInterrupt):
            print("\nbye."); break
        line = line.rstrip("\n")
        if line.strip() in (":quit", ":q", "exit"):
            print("bye."); break
        if line.strip().startswith(":strategy"):
            parts = line.strip().split()
            if len(parts) == 2 and parts[1] in ("normal", "applicative"):
                strategy = parts[1]; print(f"[strategy = {strategy}]")
            else:
                print("用法：:strategy normal|applicative")
            continue
        if line.strip().startswith(":debruijn"):
            parts = line.strip().split()
            if len(parts) == 2 and parts[1] in ("on", "off"):
                show_debruijn = (parts[1] == "on"); print(f"[debruijn = {parts[1]}]")
            else:
                print("用法：:debruijn on|off")
            continue
        if line.strip().startswith(":steps"):
            parts = line.strip().split()
            try:
                max_steps = int(parts[1]); print(f"[max_steps = {max_steps}]")
            except Exception:
                print("用法：:steps 100")
            continue
        if not line.strip() and not buf.strip():
            continue
        buf += line + "\n"
        # 簡單判斷括號平衡才執行（否則繼續讀多行）
        if buf.count("(") > buf.count(")"):
            continue
        src = buf; buf = ""
        try:
            stmts = parse_program(src)
        except SyntaxError as e:
            print(f"語法錯誤：{e}"); continue
        for st in stmts:
            if st[0] == "let":
                _, name, t = st
                env[name] = t
                print(f"let {name} = {to_string(t, unicode)}")
            else:
                _, t = st
                try:
                    full = inline_env(t, env)
                except RecursionError as e:
                    print(f"錯誤：{e}"); continue
                print(f"展開：{to_string(full, unicode)}")
                print_trace(full, strategy, max_steps, show_debruijn, unicode, decode, prefix="  ")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Lambda Calculus 解譯器（顯示完整 β-reduction 過程，有名稱/De Bruijn 雙顯示）")
    ap.add_argument("file", nargs="?", help=".lc 程式檔；不給則進入 REPL")
    ap.add_argument("-e", "--expr", default=None, help="直接求值一個式子，如 -e \"(\\x.x) y\"")
    ap.add_argument("--strategy", choices=["normal", "applicative"], default="normal",
                    help="normal=最左最外 (保證找到 normal form)，applicative=最左最內 (貼近嚴格求值)")
    ap.add_argument("--max-steps", type=int, default=100, help="最多顯示幾步（防無窮迴圈，預設 100)")
    ap.add_argument("--debruijn", action="store_true", help="同時顯示 De Bruijn index（沒名稱版）")
    ap.add_argument("--unicode", action="store_true", help="用 λ 顯示（預設用反斜線 \\）")
    ap.add_argument("--no-decode", action="store_true", help="不要把結果解讀為數字/布林")
    ap.add_argument("--prelude", default=None, help="先載入的 prelude .lc 檔")
    args = ap.parse_args(argv)

    decode = not args.no_decode
    if args.expr is not None:
        if args.prelude:
            with open(args.prelude, encoding="utf-8") as f:
                pre = f.read()
            env_stmts = parse_program(pre)
            env = {}
            for st in env_stmts:
                if st[0] == "let":
                    env[st[1]] = st[2]
            t = parse_term(args.expr)
            full = inline_env(t, env)
            print(f"輸入：{to_string(t, args.unicode)}")
            print(f"展開：{to_string(full, args.unicode)}")
            print_trace(full, args.strategy, args.max_steps, args.debruijn, args.unicode, decode)
        else:
            t = parse_term(args.expr)
            print(f"輸入：{to_string(t, args.unicode)}")
            print_trace(t, args.strategy, args.max_steps, args.debruijn, args.unicode, decode)
        return
    if args.file:
        srcs = []
        if args.prelude:
            with open(args.prelude, encoding="utf-8") as f:
                srcs.append(f.read())
        with open(args.file, encoding="utf-8") as f:
            srcs.append(f.read())
        run_program("\n".join(srcs), args.strategy, args.max_steps, args.debruijn, args.unicode, decode)
        return
    repl(args.strategy, args.max_steps, args.debruijn, args.unicode, decode)

if __name__ == "__main__":
    main()
