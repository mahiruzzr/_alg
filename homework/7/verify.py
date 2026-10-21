"""獨立驗證：用 Python 的 math.comb / 自己的 LCS DP 交叉檢查 C++ 的輸出。

用法： python verify.py
"""

import math
import os
import random
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
DIFF_EXE = os.path.join(BUILD, "diff_main.exe")
CNK_EXE = os.path.join(BUILD, "cnk.exe")


def run(exe, *args):
    r = subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"{exe} {' '.join(args)} failed: {r.returncode}\n{r.stderr}")
    return r.stdout


def lcs_len(a, b):
    n, m = len(a), len(b)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [0] * (m + 1)
        ai = a[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[m]


def parse_and_apply(a_lines, diff_text):
    hunks = []
    cur = None
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            m = re.match(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@", line)
            if not m:
                cur = None  # e.g. "@@ files are identical @@"
                continue
            cur = {
                "a_start": int(m.group(1)) - 1,
                "a_count": int(m.group(2)),
                "b_start": int(m.group(3)) - 1,
                "b_count": int(m.group(4)),
                "lines": [],
            }
            hunks.append(cur)
        elif line.startswith("--- ") or line.startswith("+++ "):
            continue
        elif cur is not None:
            cur["lines"].append(line)

    out = []
    pos = 0
    for h in hunks:
        while pos < h["a_start"]:
            out.append(a_lines[pos])
            pos += 1
        used_a = used_b = 0
        for raw in h["lines"]:
            tag, content = raw[0], raw[1:]
            if tag == " ":
                if a_lines[pos] != content:
                    raise AssertionError(f"context mismatch at {pos}: {a_lines[pos]!r} != {content!r}")
                out.append(content)
                pos += 1
                used_a += 1
                used_b += 1
            elif tag == "-":
                if a_lines[pos] != content:
                    raise AssertionError(f"delete mismatch at {pos}: {a_lines[pos]!r} != {content!r}")
                pos += 1
                used_a += 1
            elif tag == "+":
                out.append(content)
                used_b += 1
            else:
                raise AssertionError("unexpected diff line: " + raw)
        if used_a != h["a_count"] or used_b != h["b_count"]:
            raise AssertionError(
                f"hunk count mismatch: a {used_a}/{h['a_count']} b {used_b}/{h['b_count']}"
            )
    while pos < len(a_lines):
        out.append(a_lines[pos])
        pos += 1
    return out


def check_cnk():
    cases = [(5, 2), (7, 3), (12, 5), (60, 30), (75, 37), (100, 50), (200, 100), (300, 150)]
    for n, k in cases:
        text = run(CNK_EXE, "big", str(n), str(k))
        nums = re.findall(r"^\s*(?:DP \(bottom-up \+ BigUInt\)|closed-form)\s*:\s*(\d+)\s*$", text, re.M)
        if len(nums) != 2:
            raise AssertionError(f"cannot parse cnk output for {n},{k}:\n{text}")
        expected = str(math.comb(n, k))
        if nums[0] != expected or nums[1] != expected:
            raise AssertionError(f"C({n},{k}) mismatch: {nums} vs {expected}")
        print(f"  C({n},{k}) OK ({len(expected)} digits)")


def check_diff_once(a_lines, b_lines, tmpdir):
    pa = os.path.join(tmpdir, "a.txt")
    pb = os.path.join(tmpdir, "b.txt")
    with open(pa, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(a_lines) + ("\n" if a_lines else ""))
    with open(pb, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(b_lines) + ("\n" if b_lines else ""))

    minimum = len(a_lines) + len(b_lines) - 2 * lcs_len(a_lines, b_lines)
    for mode in ("dp", "myers"):
        out = run(DIFF_EXE, "file", pa, pb, mode)
        rebuilt = parse_and_apply(a_lines, out)
        if rebuilt != b_lines:
            raise AssertionError(f"{mode}: rebuilt text differs from B")
        dels = sum(1 for ln in out.splitlines() if ln.startswith("-") and not ln.startswith("--- "))
        ins = sum(1 for ln in out.splitlines() if ln.startswith("+") and not ln.startswith("+++ "))
        if dels + ins != minimum:
            raise AssertionError(f"{mode}: not minimal: {dels}+{ins} vs {minimum}")


def check_diff():
    random.seed(7)
    with tempfile.TemporaryDirectory() as td:
        for t in range(60):
            n = random.randint(1, 60)
            m = random.randint(1, 60)
            pool = [f"line {i}" for i in range(8)]
            a = [random.choice(pool) for _ in range(n)]
            b = [random.choice(pool) for _ in range(m)]
            check_diff_once(a, b, td)
        # 相似檔案（只改幾行）
        for t in range(20):
            n = random.randint(10, 120)
            a = [f"code line {i} // {random.randint(0, 5)}" for i in range(n)]
            b = list(a)
            for _ in range(random.randint(0, 6)):
                if not b:
                    break
                p = random.randrange(len(b))
                action = random.randrange(3)
                if action == 0:
                    b[p] = b[p] + " changed"
                elif action == 1:
                    b.insert(p, "inserted")
                else:
                    b.pop(p)
            check_diff_once(a, b, td)
    print("  diff: 80 random pairs OK (valid reconstruction + minimal edit count, both algorithms)")


def main():
    for exe in (DIFF_EXE, CNK_EXE):
        if not os.path.exists(exe):
            print(f"missing {exe}; build first (mingw32-make)", file=sys.stderr)
            return 1
    print("[1] C(n,k) vs math.comb")
    check_cnk()
    print("[2] diff vs independent LCS DP")
    check_diff()
    print("ALL VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
