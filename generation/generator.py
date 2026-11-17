from generation.config import (
    GRID_HEIGHT,
    GRID_WIDTH,
    SAVE,
    ITERATION,
    VIEW,
    ANIMATION,
    GENERATION_METHOD,
    AGENT_MODE,
    AGENT_STEPS,
    AGENT_TURN_PROBABILITY,
    AGENT_LOOP_PROBABILITY,
    AGENT_BRANCH_PROBABILITY,
    AGENT_COUNT,
    TARGET_LOOPS,
    CA_USE_FIXED_TUNNELS,
    POST_PROCESSING_MODE,
)
from generation.data.save import save_matrix_to_csv
from generation.verificator.tunnel_verificator import get_verification_report
from generation.algorithms.ca import (
    clone_grid,
    create_ca_grid,
    generate_tunnel_ca,
    grid_to_matrix,
)
from generation.algorithms.longest_path import keep_largest_connected_component
from generation.algorithms.digging_agent import generate_with_digging_agent
from generation.view.start_cell import find_start_cell


def print_section(title):
    print(f"\n=== {title} ===")


def print_key_value(label, value, label_width=28):
    print(f"{label:<{label_width}}: {value}")


def format_bool(value):
    return "oui" if value else "non"


def format_status(value):
    return "[OK]" if value else "[KO]"


def format_start_position(start_position):
    if start_position is None:
        return "introuvable"

    column, row = start_position
    return f"(col={column}, row={row})"


def format_2x2_positions(positions, preview_limit=8):
    if not positions:
        return "aucun"

    preview = ", ".join(str(position) for position in positions[:preview_limit])

    if len(positions) > preview_limit:
        preview += ", ..."

    return f"{len(positions)} -> {preview}"


def count_matrix_cells(matrix):
    tunnel_cells = sum(row.count(0) for row in matrix)
    wall_cells = sum(row.count(1) for row in matrix)
    return tunnel_cells, wall_cells


def print_generation_summary(method, matrix, start_position, view, save, animation):
    tunnel_cells, wall_cells = count_matrix_cells(matrix)
    height = len(matrix)
    width = len(matrix[0]) if matrix else 0

    print_section("Generation")
    print_key_value("Methode", method)
    print_key_value("Taille de la grille", f"{width} x {height}")
    print_key_value("Animation", format_bool(animation))
    print_key_value("Affichage", format_bool(view))
    print_key_value("Sauvegarde CSV", format_bool(save))
    print_key_value("Post-traitement", POST_PROCESSING_MODE)
    print_key_value("Position de depart", format_start_position(start_position))
    print_key_value("Cellules tunnel", tunnel_cells)
    print_key_value("Cellules mur", wall_cells)

    if method == "ca":
        print_key_value("Iterations minimales CA", ITERATION)
        print_key_value("Tunnels imposes", format_bool(CA_USE_FIXED_TUNNELS))
    elif method == "agent":
        print_key_value("Mode agent", AGENT_MODE)
        print_key_value("Nombre d'agents", AGENT_COUNT)
        print_key_value("Nombre de pas", AGENT_STEPS)
        print_key_value("Boucles cibles", TARGET_LOOPS)


def print_matrix(matrix):
    print_section("Matrice finale")

    if not matrix:
        print("Matrice vide")
        return

    print("Legende : 0=tunnel, 1=mur")

    row_label_width = max(len(str(len(matrix) - 1)), 2)
    column_header_prefix = " " * (row_label_width + 3)
    width = len(matrix[0])

    if width >= 10:
        tens = "".join(str((column // 10) % 10) for column in range(width))
        print(f"{column_header_prefix}{tens}")

    units = "".join(str(column % 10) for column in range(width))
    print(f"{column_header_prefix}{units}")

    for row_index, row in enumerate(matrix):
        row_values = "".join(str(value) for value in row)
        print(f"{row_index:>{row_label_width}} | {row_values}")


def print_convergence_report(convergence_report):
    if convergence_report is None:
        return

    print_section("Automate cellulaire")
    print_key_value("Convergence", format_status(convergence_report["has_converged"]))
    print_key_value("Iterations totales", convergence_report["iterations"])
    print_key_value(
        "Iterations supplementaires",
        convergence_report["extra_iterations"],
    )
    print_key_value(
        "Differences dernier pas",
        convergence_report["difference_count"],
    )


def print_verification_report(verif):
    print_section("Verification")
    print_key_value("Tunnel connecte", format_status(verif["is_connected_4"]))
    print_key_value("Regle largeur 1", format_status(verif["has_width_one"]))
    print_key_value("Tunnel valide", format_status(verif["is_valid"]))
    print_key_value(
        "Carres pleins 2x2",
        format_2x2_positions(verif["full_2x2_positions"]),
    )


def prepare_output_grid(grid):
    output_grid = clone_grid(grid)

    if POST_PROCESSING_MODE == "largest_component":
        keep_largest_connected_component(output_grid)

    elif POST_PROCESSING_MODE == "connect_components":
        from generation.algorithms.connect_components import connect_all_components

        connect_all_components(output_grid)

    elif POST_PROCESSING_MODE == "none":
        pass

    else:
        raise ValueError(
            f"Unknown POST_PROCESSING_MODE: {POST_PROCESSING_MODE}. "
            "Use 'largest_component', 'connect_components' or 'none'."
        )

    return output_grid


def get_start_position(grid):
    start = find_start_cell(grid)

    if start is not None:
        x, y = start
        return y, x

    return None


def generate_tunnel_agent(agent_mode=AGENT_MODE):
    return generate_with_digging_agent(
        n=GRID_WIDTH,
        m=GRID_HEIGHT,
        steps=AGENT_STEPS,
        turn_probability=AGENT_TURN_PROBABILITY,
        loop_probability=AGENT_LOOP_PROBABILITY,
        branch_probability=AGENT_BRANCH_PROBABILITY,
        mode=agent_mode,
        target_loops=TARGET_LOOPS,
        agent_count=AGENT_COUNT,
    )


def run_ca_generation(animation):
    fixed_tunnels = None

    if CA_USE_FIXED_TUNNELS:
        from generation.view.fixed_tunnel_selector import select_fixed_tunnels

        fixed_tunnels = select_fixed_tunnels(GRID_WIDTH, GRID_HEIGHT)

    if animation:
        try:
            from generation.view.animation import animate_automaton
        except ModuleNotFoundError as exc:
            print(f"[WARN] Animation indisponible ({exc}). Generation sans animation.")
            return generate_tunnel_ca(
                return_details=True,
                fixed_tunnels=fixed_tunnels,
            )

        return animate_automaton(
            create_ca_grid(
                GRID_WIDTH,
                GRID_HEIGHT,
                fixed_tunnels=fixed_tunnels,
            ),
            iterations=ITERATION,
            interval=500,
            post_processing_mode=POST_PROCESSING_MODE,
            fixed_tunnels=fixed_tunnels,
        )

    return generate_tunnel_ca(
        return_details=True,
        fixed_tunnels=fixed_tunnels,
    )


def run_agent_generation(animation, agent_mode=AGENT_MODE):
    if animation:
        from generation.view.animation import animate_digging_agent

        return animate_digging_agent(
            n=GRID_WIDTH,
            m=GRID_HEIGHT,
            steps=AGENT_STEPS,
            turn_probability=AGENT_TURN_PROBABILITY,
            loop_probability=AGENT_LOOP_PROBABILITY,
            branch_probability=AGENT_BRANCH_PROBABILITY,
            mode=agent_mode,
            target_loops=TARGET_LOOPS,
            agent_count=AGENT_COUNT,
            seed=None,
            interval=120,
            show_post_processing=True,
        )

    return generate_tunnel_agent(agent_mode=agent_mode)


def generation_tunnel(
    method=None,
    view=VIEW,
    save=SAVE,
    verbose=True,
    animation=ANIMATION,
    agent_mode=AGENT_MODE,
):
    if method is None:
        method = GENERATION_METHOD

    if method == "ca":
        grid, convergence_report = run_ca_generation(animation)

    elif method == "agent":
        convergence_report = None
        grid = run_agent_generation(animation, agent_mode=agent_mode)

    else:
        raise ValueError(f"Unknown generation method: {method}. Use 'ca' or 'agent'.")

    if animation and method == "ca":
        output_grid = grid
    else:
        output_grid = prepare_output_grid(grid)

    matrix = grid_to_matrix(output_grid)
    start_position = get_start_position(output_grid)

    if verbose:
        print_generation_summary(
            method,
            matrix,
            start_position,
            view=view,
            save=save,
            animation=animation,
        )
        print_matrix(matrix)

    if save:
        save_matrix_to_csv(
            matrix,
            GRID_WIDTH,
            GRID_HEIGHT,
            start_position,
            method=method,
        )

    if view and not animation:
        try:
            from generation.view.plot import plot
        except ModuleNotFoundError as exc:
            if verbose:
                print(f"[WARN] Affichage indisponible ({exc}).")
        else:
            plot(matrix)

    verif = get_verification_report(output_grid)

    if verbose:
        print_convergence_report(convergence_report)
        print_verification_report(verif)

    return output_grid
