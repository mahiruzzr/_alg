"""lambda_interp 的單元測試：python -m pytest test_lambda.py -v"""
import lambda_interp as L


def ev(expr_src, strategy="normal", max_steps=200, env=None):
    env = {} if env is None else env
    t = L.parse_term(expr_src)
    full = L.inline_env(t, env)
    steps, infos, status = L.evaluate_trace(full, strategy, max_steps)
    return steps, status


def load_prelude():
    env = {}
    for st in L.parse_program(open("examples/prelude.lc", encoding="utf-8").read()):
        if st[0] == "let":
            env[st[1]] = st[2]
    return env


def test_identity():
    steps, status = ev(r"(\x.x) y")
    assert status == "normal"
    assert L.to_string(steps[-1]) == "y"


def test_k_combinator():
    steps, status = ev(r"(\x.\y.x) a b")
    assert status == "normal" and L.to_string(steps[-1]) == "a"


def test_capture_avoiding():
    # (λx.λy.x y) y 不可把自由 y 捕捉，必須 α-conversion
    steps, infos, status = L.evaluate_trace(L.parse_term(r"(\x.\y.x y) y"), "normal", 10)
    assert status == "normal"
    assert any("alpha-conversion" in i for i in infos), infos
    assert L.to_string(steps[-1]) != r"\y.y y"  # 錯誤（被捕捉）的結果


def test_church_add():
    env = load_prelude()
    steps, status = ev("ADD 2 3", env=env)
    assert status == "normal"
    assert L.decode_church_numeral(steps[-1]) == 5


def test_church_mult():
    env = load_prelude()
    steps, status = ev("MULT 2 3", env=env)
    assert status == "normal"
    assert L.decode_church_numeral(steps[-1]) == 6


def test_bool_not():
    env = load_prelude()
    steps, status = ev("NOT TRUE", env=env)
    assert status == "normal"
    assert L.decode_church_bool(steps[-1]) is False


def test_omega_diverges():
    steps, infos, status = L.evaluate_trace(L.parse_term(r"(\x.x x) (\x.x x)"), "normal", 10)
    assert status == "limit"


def test_strategy_difference():
    # (λx.y) Ω：normal 1 步得 y；applicative 發散
    t = L.parse_term(r"(\x.y) ((\x.x x) (\x.x x))")
    s1, _, st1 = L.evaluate_trace(t, "normal", 10)
    assert st1 == "normal" and L.to_string(s1[-1]) == "y"
    _, _, st2 = L.evaluate_trace(t, "applicative", 10)
    assert st2 == "limit"


def test_factorial_2():
    env = load_prelude()
    fact = L.parse_term(r"Y (\f.\n.IF (ISZERO n) 1 (MULT n (f (PRED n))))")
    full_fact = L.inline_env(fact, env)
    env2 = dict(env)
    env2["FACT"] = fact
    steps, status = ev("FACT 2", env=env2, max_steps=500)
    assert status == "normal"
    assert L.decode_church_numeral(steps[-1]) == 2


def test_debruijn_roundtrip():
    t = L.parse_term(r"\x.\y.x y")
    db = L.to_debruijn(t)
    back = L.from_debruijn(db)
    assert L.alpha_equal(t, back)
    assert L.db_to_string(db) == r"(\.(\.(1 0)))"
