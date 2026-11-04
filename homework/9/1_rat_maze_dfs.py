"""問題 1：老鼠走迷宮 (DFS + 回溯)

狀態 = 座標 (y, x)；動作 = 上下左右走一步；目標 = 走到 E。
"""
import sys

sys.setrecursionlimit(10000)

MAZE = [
    "#############",
    "#S..#.......#",
    "#.#.#.#####.#",
    "#.#...#...#.#",
    "#.#####.#.#.#",
    "#.......#...#",
    "#.#######.###",
    "#.#.....#...#",
    "#.#.###.###.#",
    "#...#.......#",
    "#######.#####",
    "#E......#####",
    "#############",
]

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 上 右 下 左


def find(maze, ch):
    for y, row in enumerate(maze):
        if ch in row:
            return y, row.index(ch)
    raise ValueError(f"找不到 {ch}")


def solve_dfs(maze):
    start, goal = find(maze, "S"), find(maze, "E")
    visited, path = set(), []
    tries = 0

    def dfs(y, x):
        nonlocal tries
        tries += 1
        visited.add((y, x))
        path.append((y, x))               # 深入 = push
        if (y, x) == goal:
            return True                   # 成功沿遞迴逐層回傳
        for dy, dx in DIRS:
            ny, nx = y + dy, x + dx
            if maze[ny][nx] != "#" and (ny, nx) not in visited:
                if dfs(ny, nx):
                    return True
        path.pop()                        # 死路 = pop（回溯）
        return False

    ok = dfs(*start)
    return (path if ok else None), tries


def show(maze, path):
    grid = [list(r) for r in maze]
    for y, x in path[1:-1]:
        grid[y][x] = "*"
    print("\n".join("".join(r) for r in grid))


if __name__ == "__main__":
    path, tries = solve_dfs(MAZE)
    if path:
        print(f"找到路徑！長度 = {len(path)} 格，共嘗試 {tries} 格\n")
        show(MAZE, path)
    else:
        print("此迷宮無解")
