from generation.generator import generation_tunnel


def test_no_full_2x2():
    for method in ["ca", "agent"]:
        grid = generation_tunnel(
            method=method, view=False, save=False, verbose=False, animation=False
        )

        for i in range(len(grid) - 1):
            for j in range(len(grid[0]) - 1):
                square = [
                    grid[i][j].state,
                    grid[i + 1][j].state,
                    grid[i][j + 1].state,
                    grid[i + 1][j + 1].state,
                ]

                assert not all(square), (
                    f"Carré 2x2 plein détecté avec method={method} en position ({i}, {j})"
                )


def test_connected_tunnel():
    for method in ["ca", "agent"]:
        grid = generation_tunnel(
            method=method, view=False, save=False, verbose=False, animation=False
        )

        visited = set()
        stack = [(0, 0)]

        # trouver un point de départ valide
        found = False
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j].state:
                    stack = [(i, j)]
                    found = True
                    break
            if found:
                break

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue

            visited.add((x, y))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    if grid[nx][ny].state:
                        stack.append((nx, ny))

        total_tunnel = sum(cell.state for row in grid for cell in row)

        assert len(visited) == total_tunnel, "Le tunnel n'est pas entièrement connecté"
