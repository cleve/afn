def plot_tsp_solution(base_elements, route: list[str], output_path: str, close_loop: bool = True):
    """Save a PNG plot with city points and the proposed TSP cycle."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError('matplotlib is required for plotting. Install it with: pip install matplotlib') from error

    points_by_node = {
        str(int(node_id)): (x, y)
        for node_id, x, y in base_elements
    }

    missing_nodes = [node for node in route if node not in points_by_node]
    if missing_nodes:
        raise ValueError(f'Route contains nodes missing from coordinates: {missing_nodes[:5]}')

    ordered_points = [points_by_node[node] for node in route]
    if close_loop and ordered_points:
        ordered_points = ordered_points + [ordered_points[0]]

    x_values = [item[0] for item in ordered_points]
    y_values = [item[1] for item in ordered_points]

    all_x = [item[1] for item in base_elements]
    all_y = [item[2] for item in base_elements]

    figure = plt.figure(figsize=(10, 8))
    axis = figure.add_subplot(1, 1, 1)
    axis.scatter(all_x, all_y, color='#1f77b4', s=22, zorder=3)
    axis.plot(x_values, y_values, color='#d62728', linewidth=1.6, zorder=2)

    for node, (x_coord, y_coord) in points_by_node.items():
        axis.text(x_coord, y_coord, node, fontsize=7, alpha=0.8)

    axis.set_title('AFN Proposed TSP Cycle')
    axis.set_xlabel('X')
    axis.set_ylabel('Y')
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)