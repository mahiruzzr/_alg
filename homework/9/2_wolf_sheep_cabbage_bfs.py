"""問題 2：狼、羊、甘藍菜過河 (BFS)

狀態 = (農夫, 狼, 羊, 菜)，0 = 左岸、1 = 右岸，共 2^4 = 16 種。
BFS 一層一層展開，第一次碰到目標就是最少渡河次數。
"""
from collections import deque

NAMES = ["狼", "羊", "菜"]
START, GOAL = (0, 0, 0, 0), (1, 1, 1, 1)


def is_legal(s):
    farmer, wolf, sheep, cabbage = s
    if wolf == sheep != farmer:       # 農夫不在：狼吃羊
        return False
    if sheep == cabbage != farmer:    # 農夫不在：羊吃菜
        return False
    return True


def neighbors(s):
    """農夫過河，可獨自、或帶一件與他同岸的東西。"""
    farmer = s[0]
    # 獨自過河
    yield (1 - farmer,) + s[1:], "農夫單獨過河"
    # 帶 i 號東西過河
    for i in range(3):
        if s[i + 1] == farmer:
            nxt = list(s)
            nxt[0] = 1 - farmer
            nxt[i + 1] = 1 - farmer
            yield tuple(nxt), f"農夫帶著{NAMES[i]}過河"


def bfs():
    frontier = deque([START])
    parent = {START: (None, "出發")}          # 兼當 visited
    expanded = 0
    while frontier:
        s = frontier.popleft()                # FIFO：同層先做完
        expanded += 1
        if s == GOAL:
            steps = []
            while s is not None:
                prev, action = parent[s]
                steps.append((action, s))
                s = prev
            return steps[::-1], expanded
        for nxt, action in neighbors(s):
            if nxt not in parent and is_legal(nxt):
                parent[nxt] = (s, action)
                frontier.append(nxt)
    return None, expanded


if __name__ == "__main__":
    steps, expanded = bfs()
    print(f"最少 {len(steps) - 1} 次渡河（BFS 共展開 {expanded} 個狀態 / 共 16 個）\n")
    for i, (action, s) in enumerate(steps):
        print(f"{i}. {action:<12} 狀態 = {s}")
