# SAT 暴力解：系統性列舉真值表
# Boolean satisfiability problem: https://en.wikipedia.org/wiki/Boolean_satisfiability_problem
#
# CNF 表示法 (DIMACS 風格，不含結尾 0)：
#   變數編號 1..n，文字 (literal) 正數表 x_i，負數表 NOT x_i
#   clause = OR，例如 [1, -2] 表 (x1 OR NOT x2)
#   clauses = AND，例如 [[1, -2], [-1, 2]] 表 (x1 OR NOT x2) AND (NOT x1 OR x2)
#
# 複雜度：O(2^n * m * k)，n=變數數，m=clause數，k=平均clause長度

from itertools import product


def assignment_from_int(n, code):
    """把 0..2^n-1 的整數轉成一組真值指派，系統性列舉用。
    code 的二進位第 i 位對應 x_{i+1}，例如 n=3, code=5 (101) -> {1:T, 2:F, 3:T}
    """
    return {i + 1: bool((code >> i) & 1) for i in range(n)}


def eval_clause(clause, assign):
    """單一 clause (OR) 是否被滿足"""
    return any(assign[abs(lit)] == (lit > 0) for lit in clause)


def eval_cnf(clauses, assign):
    """整個 CNF (AND) 是否被滿足"""
    return all(eval_clause(c, assign) for c in clauses)


def iter_truth_table(n):
    """系統性列舉 2^n 組真值：二進位計數順序，保證不重不漏"""
    for code in range(2 ** n):
        yield code, assignment_from_int(n, code)


def solve_sat(n, clauses, verbose=False):
    """回傳第一組滿足的指派 dict，UNSAT 回傳 None"""
    for code, assign in iter_truth_table(n):
        sat = eval_cnf(clauses, assign)
        if verbose:
            bits = "".join("T" if assign[i] else "F" for i in range(1, n + 1))
            print(f"  [{code:>{len(bin(2**n)) - 2}}] {bits} -> {'SAT' if sat else '---'}")
        if sat:
            return assign
    return None


def solve_sat_all(n, clauses, limit=None):
    """回傳所有滿足的指派 (limit 可限制個數)"""
    found = []
    for _, assign in iter_truth_table(n):
        if eval_cnf(clauses, assign):
            found.append(dict(assign))
            if limit is not None and len(found) >= limit:
                break
    return found


def format_assign(assign):
    return "{" + ", ".join(f"x{i}={'T' if v else 'F'}" for i, v in sorted(assign.items())) + "}"


def format_cnf(clauses):
    parts = []
    for c in clauses:
        lits = []
        for lit in c:
            v = abs(lit)
            lits.append(f"x{v}" if lit > 0 else f"~x{v}")
        parts.append("(" + " OR ".join(lits) + ")")
    return " AND ".join(parts)


if __name__ == "__main__":
    examples = [
        # (名稱, 變數數, clauses)
        ("EX1 SAT: (x1 OR x2) AND (~x1 OR x2)",
         2, [[1, 2], [-1, 2]]),
        ("EX2 UNSAT: (x1) AND (~x1)",
         1, [[1], [-1]]),
        ("EX3 SAT: (x1 OR ~x2) AND (~x1 OR x2 OR x3) AND (~x3)",
         3, [[1, -2], [-1, 2, 3], [-3]]),
    ]

    for name, n, clauses in examples:
        print(f"\n{name}")
        print(f"  CNF: {format_cnf(clauses)}")
        print(f"  真值表列舉 (共 2^{n}={2**n} 組):")
        ans = solve_sat(n, clauses, verbose=True)
        if ans is None:
            print("  結果: UNSAT（全部 2^n 組都不滿足）")
        else:
            print(f"  結果: SAT，第一組解 {format_assign(ans)}")
            all_ans = solve_sat_all(n, clauses)
            print(f"  全部解共 {len(all_ans)} 組")
