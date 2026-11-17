import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button


def has_forbidden_2x2(matrix):
    height, width = matrix.shape

    for x in range(height - 1):
        for y in range(width - 1):
            block = matrix[x : x + 2, y : y + 2]

            # 0 = tunnel
            if np.all(block == 0):
                return True

    return False


def select_fixed_tunnels(n, m):
    fixed_tunnels = set()

    # 1 = mur noir, 0 = tunnel vert
    matrix = np.ones((n, m), dtype=int)

    cmap = ListedColormap(["#00CC66", "#222222"])

    fig, ax = plt.subplots(figsize=(7, 7))
    plt.subplots_adjust(top=0.88, bottom=0.22)

    image = ax.imshow(
        matrix,
        cmap=cmap,
        vmin=0,
        vmax=1,
        interpolation="nearest",
    )

    ax.set_title(
        "Clic gauche + drag pour ajouter | Clic droit + drag pour enlever",
        pad=10,
    )
    ax.axis("off")

    # Position du bouton
    button_x = 0.38
    button_y = 0.04
    button_width = 0.24
    button_height = 0.07

    button_ax = plt.axes([button_x, button_y, button_width, button_height])
    validate_button = Button(button_ax, "Valider")

    # Position réelle de la grille
    ax_pos = ax.get_position()
    grid_bottom_y = ax_pos.y0
    button_top_y = button_y + button_height

    # Message exactement entre la grille et le bouton
    message_y = (grid_bottom_y + button_top_y) / 2

    message = fig.text(
        0.5,
        message_y,
        "",
        ha="center",
        va="center",
        fontsize=10,
    )

    is_valid = True
    is_dragging = False
    last_drawn_position = None
    current_mode = None  # "add" ou "remove"

    def update_validation_state():
        nonlocal is_valid

        if has_forbidden_2x2(matrix):
            is_valid = False
            message.set_text(
                "Attention : largeur 2 interdite, enlève au moins une case du carré 2x2."
            )
            validate_button.label.set_color("gray")
            button_ax.set_alpha(0.35)
        else:
            is_valid = True
            message.set_text("")
            validate_button.label.set_color("black")
            button_ax.set_alpha(1.0)

        fig.canvas.draw_idle()

    def bresenham_line(x0, y0, x1, y1):
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points

    def set_tunnel_cell(x, y):
        if not (0 <= x < n and 0 <= y < m):
            return
        if (x, y) not in fixed_tunnels:
            fixed_tunnels.add((x, y))
            matrix[x][y] = 0

    def unset_tunnel_cell(x, y):
        if not (0 <= x < n and 0 <= y < m):
            return
        if (x, y) in fixed_tunnels:
            fixed_tunnels.remove((x, y))
            matrix[x][y] = 1

    def on_press(event):
        nonlocal is_dragging, last_drawn_position, current_mode

        if event.inaxes != ax or event.button not in [1, 3]:
            return

        y = int(round(event.xdata))
        x = int(round(event.ydata))

        if not (0 <= x < n and 0 <= y < m):
            return

        is_dragging = True
        current_mode = "add" if event.button == 1 else "remove"
        last_drawn_position = (x, y)

        if current_mode == "add":
            set_tunnel_cell(x, y)
        else:
            unset_tunnel_cell(x, y)

        image.set_data(matrix)
        update_validation_state()

    def on_motion(event):
        nonlocal is_dragging, last_drawn_position, current_mode

        if not is_dragging or event.inaxes != ax or last_drawn_position is None:
            return

        y = int(round(event.xdata))
        x = int(round(event.ydata))

        if not (0 <= x < n and 0 <= y < m):
            return

        if (x, y) == last_drawn_position:
            return

        x0, y0 = last_drawn_position
        line_cells = bresenham_line(x0, y0, x, y)

        for cell_x, cell_y in line_cells:
            if current_mode == "add":
                set_tunnel_cell(cell_x, cell_y)
            else:
                unset_tunnel_cell(cell_x, cell_y)

        last_drawn_position = (x, y)
        image.set_data(matrix)
        update_validation_state()

    def on_release(event):
        nonlocal is_dragging, current_mode
        is_dragging = False
        current_mode = None

    def on_validate(event):
        if not is_valid:
            message.set_text(
                "Impossible de valider : corrige d’abord le carré 2x2 de tunnels."
            )
            fig.canvas.draw_idle()
            return

        plt.close(fig)

    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)
    validate_button.on_clicked(on_validate)

    update_validation_state()
    plt.show()

    return fixed_tunnels
