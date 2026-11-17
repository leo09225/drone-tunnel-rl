def count_grid_differences(grid_1, grid_2):
    differences = 0

    for x in range(len(grid_1)):
        for y in range(len(grid_1[0])):
            if grid_1[x][y].state != grid_2[x][y].state:
                differences += 1

    return differences


def has_converged(grid_1, grid_2):
    return count_grid_differences(grid_1, grid_2) == 0
