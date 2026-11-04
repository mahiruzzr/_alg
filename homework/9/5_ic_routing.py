"""問題 5：IC 設計中的電路繞線 (Routing)

把晶片的一層金屬看成 R x C 的格子：
  * 每條 net 要把兩個接腳 (pin) 連起來
  * 不同 net 的導線不能共用同一格、也不能穿過牆 (blockage) 或別條 net 的接腳

本檔依序示範（由淺到深）：
  A. 單一 net 的三種格子搜尋：Lee (BFS 水波)、Hadlock (0/1 BFS)、A*
  B. 多條 net 逐條繞：結果會受「繞線順序」影響（net ordering）
  C. Rip-up & Reroute：失敗時撕掉擋路的線，先讓失敗者過，再重繞被撕的
  D. PathFinder（negotiated congestion）：先允許重疊，再靠「漲價」讓大家談判出合法解
"""
import heapq
import itertools
from collections import deque

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(cell, R, C):
    for dy, dx in DIRS:
        y, x = cell[0] + dy, cell[1] + dx
        if 0 <= y < R and 0 <= x < C:
            yield (y, x)


def rebuild(parent, cur):
    path = []
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]


# ------------------------------------------------------------------
# A. 單一 net 的三種搜尋法。回傳 (路徑, 展開格數)；blocked = 不能走的格子
# ------------------------------------------------------------------
def lee(R, C, blocked, src, dst):
    """Lee 演算法 = BFS 水波：每圈往外擴一格，碰到 dst 後沿 parent 回溯。"""
    q, parent, expanded = deque([src]), {src: None}, 0
    while q:
        cur = q.popleft()
        expanded += 1
        if cur == dst:
            return rebuild(parent, cur), expanded
        for nxt in neighbors(cur, R, C):
            if nxt not in blocked and nxt not in parent:
                parent[nxt] = cur
                q.append(nxt)
    return None, expanded


def hadlock(R, C, blocked, src, dst):
    """Hadlock 演算法 = 0/1 BFS。
    往「接近目標」的步成本 0，往「遠離目標」(detour) 的步成本 1。
    路徑長度 = 曼哈頓距離 + 2 * detour 數，所以 detour 最少 = 路徑最短。"""
    dist, parent = {src: 0}, {src: None}
    dq, settled, expanded = deque([src]), set(), 0
    while dq:
        cur = dq.popleft()
        if cur in settled:
            continue
        settled.add(cur)
        expanded += 1
        if cur == dst:
            return rebuild(parent, cur), expanded
        for nxt in neighbors(cur, R, C):
            if nxt in blocked:
                continue
            w = 0 if manhattan(nxt, dst) < manhattan(cur, dst) else 1
            if dist[cur] + w < dist.get(nxt, float("inf")):
                dist[nxt] = dist[cur] + w
                parent[nxt] = cur
                (dq.appendleft if w == 0 else dq.append)(nxt)
    return None, expanded


def astar(R, C, blocked, src, dst):
    """A*：f = g + h，h 用曼哈頓距離（格子上不會高估 → 保證最短）。"""
    tie = 0
    heap = [(manhattan(src, dst), tie, 0, src)]
    g_best, parent, closed = {src: 0}, {src: None}, set()
    while heap:
        _, _, g, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        if cur == dst:
            return rebuild(parent, cur), len(closed)
        for nxt in neighbors(cur, R, C):
            if nxt in blocked:
                continue
            if g + 1 < g_best.get(nxt, float("inf")):
                g_best[nxt] = g + 1
                parent[nxt] = cur
                tie += 1
                heapq.heappush(heap, (g + 1 + manhattan(nxt, dst), tie, g + 1, nxt))
    return None, len(closed)


def render(R, C, walls, nets, paths):
    """牆 #、接腳大寫字母 A B C…、導線小寫字母。"""
    g = [["." for _ in range(C)] for _ in range(R)]
    for y, x in walls:
        g[y][x] = "#"
    for i, p in paths.items():
        for y, x in p:
            g[y][x] = chr(ord("a") + i)
    for i, (s, t) in enumerate(nets):
        for y, x in (s, t):
            g[y][x] = chr(ord("A") + i)
    return "\n".join(" ".join(r) for r in g)


def demo_single_net():
    R, C = 10, 14
    walls = {(r, 4) for r in range(1, 8)} | {(r, 9) for r in range(2, 10)} | {(3, 6), (3, 7), (5, 6), (5, 7)}
    src, dst = (8, 1), (7, 12)
    print("=== A. 單一 net：Lee / Hadlock / A* ===")
    for name, fn in [("Lee", lee), ("Hadlock", hadlock), ("A*", astar)]:
        path, expanded = fn(R, C, set(walls), src, dst)
        print(f"{name:<8} 路徑長 {len(path) - 1:>2} 步，展開 {expanded:>3} 格（全圖可走 {R * C - len(walls)} 格）")
    print()
    print(render(R, C, walls, [(src, dst)], {0: path}))


# ------------------------------------------------------------------
# B~D. 多條 net。測試用的 7x7 例子（以隨機搜尋挑出：照 A→B→C 順序繞會失敗）
# ------------------------------------------------------------------
R, C = 7, 7
WALLS = {(1, 0), (1, 3), (2, 4), (3, 0), (3, 5)}
NETS = [((0, 3), (0, 6)), ((0, 0), (5, 6)), ((1, 4), (5, 4))]   # A, B, C


def all_pins(nets):
    return {p for n in nets for p in n}


def route_in_order(order, search=astar, verbose=True):
    """依照給定順序逐條繞，前面繞好的線變成後面的障礙。"""
    used, paths = set(), {}
    pins = all_pins(NETS)
    for i in order:
        s, t = NETS[i]
        blocked = WALLS | used | (pins - {s, t})
        path, _ = search(R, C, blocked, s, t)
        if path is None:
            if verbose:
                print(f"  net {chr(65 + i)} 繞不通！（前面已繞的線把路擋死了）")
            return None
        paths[i] = path
        used |= set(path)
    return paths


def demo_ordering():
    print("\n=== B. 多條 net 逐條繞：順序很重要 ===")
    first_ok = None
    for order in itertools.permutations(range(len(NETS))):
        name = "→".join(chr(65 + i) for i in order)
        paths = route_in_order(order, verbose=False)
        if paths:
            total = sum(len(p) - 1 for p in paths.values())
            print(f"順序 {name}：成功，總線長 {total}")
            first_ok = first_ok or (name, paths)
        else:
            print(f"順序 {name}：失敗（有 net 被前面的線擋死）")
    if first_ok:
        print(f"\n順序 {first_ok[0]} 的結果：")
        print(render(R, C, WALLS, NETS, first_ok[1]))


# ------------------------------------------------------------------
# C. Rip-up & Reroute
# ------------------------------------------------------------------
def rip_up_and_reroute(max_iter=50):
    pins = all_pins(NETS)
    paths, queue, log = {}, deque(range(len(NETS))), []
    for _ in range(max_iter):
        if not queue:
            return paths, log
        i = queue.popleft()
        s, t = NETS[i]
        used = {c for p in paths.values() for c in p}
        path, _ = astar(R, C, WALLS | used | (pins - {s, t}), s, t)
        if path is None:
            # 失敗：忽略別人的導線，算出 i 的理想路線，撕掉被它擋到的 net
            ideal, _ = astar(R, C, WALLS | (pins - {s, t}), s, t)
            if ideal is None:
                return None, log
            victims = [j for j, p in paths.items() if set(p) & set(ideal)]
            log.append(f"net {chr(65 + i)} 繞不通 → 撕掉 {[chr(65 + j) for j in victims]}")
            for j in victims:
                del paths[j]
            paths[i] = ideal
            queue.extend(victims)          # 被撕的 net 排到後面重繞
        else:
            paths[i] = path
            log.append(f"net {chr(65 + i)} 繞成功（{len(path) - 1} 步）")
    return None, log


def demo_ripup():
    print("\n=== C. Rip-up & Reroute ===")
    paths, log = rip_up_and_reroute()
    for line in log:
        print("  " + line)
    if paths:
        print(render(R, C, WALLS, NETS, paths))
        print(f"  成功，總線長 = {sum(len(p) - 1 for p in paths.values())}")


# ------------------------------------------------------------------
# D. PathFinder：協商式壅塞 (negotiated congestion)
# ------------------------------------------------------------------
def dijkstra_cost(cost, blocked, src, dst):
    """格子有各自的進入成本（壅塞越高越貴）。"""
    dist, parent, heap = {src: 0.0}, {src: None}, [(0.0, src)]
    while heap:
        d, cur = heapq.heappop(heap)
        if d > dist[cur]:
            continue
        if cur == dst:
            return rebuild(parent, cur)
        for nxt in neighbors(cur, R, C):
            if nxt in blocked:
                continue
            nd = d + cost(nxt)
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                parent[nxt] = cur
                heapq.heappush(heap, (nd, nxt))
    return None


def pathfinder(max_iter=30):
    pins = all_pins(NETS)
    hist = {}                      # 歷史壅塞：吃過虧的格子永遠比較貴
    pf = 0.0                       # 目前壅塞罰款：第 1 輪 = 0（人人只管自己的最短路），之後每輪調漲
    paths = {}
    for it in range(1, max_iter + 1):
        for i, (s, t) in enumerate(NETS):
            paths.pop(i, None)     # 撕掉自己重繞
            occ = {}
            for p in paths.values():
                for c in p:
                    occ[c] = occ.get(c, 0) + 1
            cost = lambda c: (1 + hist.get(c, 0)) * (1 + pf * occ.get(c, 0))
            paths[i] = dijkstra_cost(cost, WALLS | (pins - {s, t}), s, t)
        usage = {}
        for p in paths.values():
            for c in p:
                usage[c] = usage.get(c, 0) + 1
        over = [c for c, n in usage.items() if n > 1]
        print(f"  第 {it} 輪：超載格數 = {len(over)}")
        if not over:
            return paths
        for c in over:
            hist[c] = hist.get(c, 0) + 1
        pf = 0.5 if pf == 0 else pf * 2
    return None


def demo_pathfinder():
    print("\n=== D. PathFinder（先允許重疊，再靠漲價談判）===")
    paths = pathfinder()
    if paths:
        print(render(R, C, WALLS, NETS, paths))
        print(f"  成功，總線長 = {sum(len(p) - 1 for p in paths.values())}")


if __name__ == "__main__":
    demo_single_net()
    demo_ordering()
    demo_ripup()
    demo_pathfinder()
