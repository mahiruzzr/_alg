"""問題 4：NPC 搜尋玩家 (A*)

地圖 N = NPC、P = 玩家、# = 牆。NPC 要用最少步走到玩家身邊。
A* 每次從 priority queue 取 f(n) = g(n) + h(n) 最小的格子展開：
    g = 起點到 n 的實際步數；h = n 到目標的曼哈頓距離（不會高估 → 保證最短）。
"""
import heapq
from collections import deque

MAP = [
    "###############",
    "#N....#.......#",
    "#.###.#.#####.#",
    "#.#...#.#...#.#",
    "#.#.###.#.#.#.#",
    "#.#.....#.#...#",
    "#.#######.#####",
    "#.........#...#",
    "#.#######.#.#.#",
    "#.#.....#...#P#",
    "#...###...###.#",
    "###############",
]
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def find(grid, ch):
    for y, row in enumerate(grid):
        if ch in row:
            return y, row.index(ch)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def walkable(grid, y, x):
    return grid[y][x] != "#"


def astar(grid, start, goal):
    """回傳 (路徑, 展開格數)。"""
    tie = 0                                       # f 相同時的先後順序
    open_heap = [(manhattan(start, goal), tie, 0, start)]
    g_best = {start: 0}
    parent = {start: None}
    closed = set()
    while open_heap:
        f, _, g, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)                           # 展開 cur
        if cur == goal:
            return rebuild(parent, cur), len(closed)
        for dy, dx in DIRS:
            nxt = (cur[0] + dy, cur[1] + dx)
            if not walkable(grid, *nxt):
                continue
            ng = g + 1
            if ng < g_best.get(nxt, float("inf")):
                g_best[nxt] = ng
                parent[nxt] = cur
                tie += 1
                heapq.heappush(open_heap, (ng + manhattan(nxt, goal), tie, ng, nxt))
    return None, len(closed)


def bfs(grid, start, goal):
    """對照組：A* 把 h 設成 0 就等於 BFS。"""
    q, parent, expanded = deque([start]), {start: None}, 0
    while q:
        cur = q.popleft()
        expanded += 1
        if cur == goal:
            return rebuild(parent, cur), expanded
        for dy, dx in DIRS:
            nxt = (cur[0] + dy, cur[1] + dx)
            if walkable(grid, *nxt) and nxt not in parent:
                parent[nxt] = cur
                q.append(nxt)
    return None, expanded


def dfs(grid, start, goal):
    """對照組：DFS 找得到，但不保證最短。"""
    stack, parent, expanded = [start], {start: None}, 0
    seen = set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        expanded += 1
        if cur == goal:
            return rebuild(parent, cur), expanded
        for dy, dx in DIRS:
            nxt = (cur[0] + dy, cur[1] + dx)
            if walkable(grid, *nxt) and nxt not in seen:
                parent[nxt] = cur
                stack.append(nxt)
    return None, expanded


def rebuild(parent, cur):
    path = []
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]


def show(grid, path):
    g = [list(r) for r in grid]
    for y, x in path[1:-1]:
        g[y][x] = "*"
    print("\n".join("".join(r) for r in g))


def chase_demo(grid, npc, player, steps=6):
    """玩家一直逃，NPC 每一步重新用 A* 規劃（遊戲 AI 每幀的做法）。"""
    print("\n--- 追逐模擬：玩家每回合往遠離 NPC 的方向走一步，NPC 每回合重新 A* ---")
    for t in range(1, steps + 1):
        path, _ = astar(grid, npc, player)
        if len(path) <= 2:
            print(f"第 {t} 回合：NPC 抓到玩家了！")
            return
        npc = path[1]                              # NPC 沿路徑走一步
        best = max(
            ((player[0] + dy, player[1] + dx) for dy, dx in DIRS
             if walkable(grid, player[0] + dy, player[1] + dx)),
            key=lambda p: manhattan(p, npc),
        )
        player = best
        print(f"第 {t} 回合：NPC → {npc}，玩家 → {player}，距離（曼哈頓）= {manhattan(npc, player)}")


if __name__ == "__main__":
    start, goal = find(MAP, "N"), find(MAP, "P")
    path, exp_a = astar(MAP, start, goal)
    print(f"A* 找到路徑：{len(path) - 1} 步，展開 {exp_a} 格\n")
    show(MAP, path)

    p_b, exp_b = bfs(MAP, start, goal)
    p_d, exp_d = dfs(MAP, start, goal)
    print("\n--- 同一張地圖三種搜尋法比較 ---")
    print(f"A*  ：{len(path) - 1:>3} 步（最短）  展開 {exp_a:>3} 格")
    print(f"BFS ：{len(p_b) - 1:>3} 步（最短）  展開 {exp_b:>3} 格")
    print(f"DFS ：{len(p_d) - 1:>3} 步（不保證）展開 {exp_d:>3} 格")

    chase_demo(MAP, start, goal)
