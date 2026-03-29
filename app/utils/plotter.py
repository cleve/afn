def plot_tsp_solution(base_elements, route: list[str], output_path: str, close_loop: bool = True):
    """Save a PNG plot with city points and the proposed TSP cycle."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError('matplotlib is required for plotting. Install it with: poetry install -E plot') from error

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


def animate_fusion_process(base_elements, fusion_events, delay_seconds: float = 1.0, record_file: str | None = None):
    """Show a live educational animation of star fusion and state evolution.

    Optionally records the animation to GIF/MP4 when record_file is provided.
    """
    try:
        import matplotlib

        backend = matplotlib.get_backend().lower()
        if backend.endswith('agg'):
            for candidate in ('TkAgg', 'QtAgg', 'GTK3Agg'):
                try:
                    matplotlib.use(candidate, force=True)
                    break
                except Exception:
                    continue

        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
    except ImportError as error:
        raise RuntimeError('matplotlib is required for educational mode. Install it with: poetry install -E plot') from error

    if delay_seconds <= 0:
        raise ValueError('delay_seconds must be greater than 0')

    def _normalize_node_id(node_id) -> str:
        if isinstance(node_id, str):
            try:
                return str(int(float(node_id)))
            except ValueError:
                return node_id
        try:
            return str(int(node_id))
        except (TypeError, ValueError):
            return str(node_id)

    points_by_node = {
        _normalize_node_id(node_id): (x, y)
        for node_id, x, y in base_elements
    }

    all_x = [item[1] for item in base_elements]
    all_y = [item[2] for item in base_elements]

    figure, (axis_map, axis_state, axis_elements) = plt.subplots(1, 3, figsize=(20, 6))

    active_original_points, = axis_map.plot(
        all_x,
        all_y,
        linestyle='None',
        marker='o',
        color='#2b8cbe',
        markersize=6,
        zorder=2,
        label='Active original nodes',
    )
    fused_original_points, = axis_map.plot(
        [],
        [],
        linestyle='None',
        marker='o',
        color='#8a8a8a',
        markersize=6,
        zorder=2,
        label='Fusionated original nodes',
    )
    new_elements_points, = axis_map.plot(
        [],
        [],
        linestyle='None',
        marker='o',
        color='#f72585',
        markersize=10,
        zorder=3,
        label='New fused elements',
    )
    current_new_element, = axis_map.plot(
        [],
        [],
        linestyle='None',
        marker='*',
        color='#ffba08',
        markersize=15,
        zorder=6,
    )

    for node, (x_coord, y_coord) in points_by_node.items():
        axis_map.text(x_coord, y_coord, node, fontsize=7, alpha=0.8)

    axis_map.set_title('Fusion process (educative view)')
    axis_map.set_xlabel('X')
    axis_map.set_ylabel('Y')
    axis_map.grid(True, alpha=0.2)
    axis_map.legend(loc='lower right', fontsize=8)

    if not fusion_events:
        axis_map.text(0.5, 0.5, 'No fusion events available', transform=axis_map.transAxes, ha='center', va='center')
        axis_state.set_axis_off()
        axis_elements.set_axis_off()
        figure.tight_layout()
        plt.show(block=True)
        return

    steps = list(range(1, len(fusion_events) + 1))
    temperatures = [event['temperature'] for event in fusion_events]
    pressures = [event['pressure'] for event in fusion_events]
    densities = [event['density'] for event in fusion_events]

    line_temp, = axis_state.plot([], [], color='#d62728', label='Temperature', linewidth=2)
    line_pressure, = axis_state.plot([], [], color='#2ca02c', label='Pressure', linewidth=2)
    line_density, = axis_state.plot([], [], color='#ff7f0e', label='Density', linewidth=2)

    marker_temp, = axis_state.plot([], [], marker='o', color='#d62728')
    marker_pressure, = axis_state.plot([], [], marker='o', color='#2ca02c')
    marker_density, = axis_state.plot([], [], marker='o', color='#ff7f0e')

    axis_state.set_title('Star life evolution by fusion event')
    axis_state.set_xlabel('Fusion event')
    axis_state.set_ylabel('State value')
    axis_state.grid(True, alpha=0.2)
    axis_state.legend(loc='upper right')

    max_y = max(
        max(temperatures) if temperatures else 0,
        max(pressures) if pressures else 0,
        max(densities) if densities else 0,
    )
    axis_state.set_xlim(1, max(2, len(steps)))
    axis_state.set_ylim(0, max_y * 1.15 if max_y > 0 else 1.0)

    # --- Element type evolution panel ---
    h_counts  = [e['type_counts'].get('HIDROGEN', 0) for e in fusion_events]
    he_counts = [e['type_counts'].get('HELIUM',   0) for e in fusion_events]
    c_counts  = [e['type_counts'].get('CARBON',   0) for e in fusion_events]

    line_h,  = axis_elements.plot([], [], color='#00b4d8', linewidth=2, label='Hydrogen (H)')
    line_he, = axis_elements.plot([], [], color='#f4a261', linewidth=2, label='Helium (He)')
    line_c,  = axis_elements.plot([], [], color='#e63946', linewidth=2, label='Carbon (C)')
    marker_h,  = axis_elements.plot([], [], marker='o', color='#00b4d8', markersize=6)
    marker_he, = axis_elements.plot([], [], marker='o', color='#f4a261', markersize=6)
    marker_c,  = axis_elements.plot([], [], marker='o', color='#e63946', markersize=6)

    axis_elements.set_title('Element type evolution')
    axis_elements.set_xlabel('Fusion event')
    axis_elements.set_ylabel('Count')
    axis_elements.set_xlim(1, max(2, len(steps)))
    axis_elements.set_ylim(0, max(len(fusion_events), 1) * 1.15)
    axis_elements.grid(True, alpha=0.2)
    axis_elements.legend(loc='upper right')

    type_didactic = axis_elements.text(
        0.02, 0.02, '',
        transform=axis_elements.transAxes,
        va='bottom', ha='left', fontsize=9,
        bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': 0.75}
    )

    current_pair_line, = axis_map.plot([], [], color='#d62728', linewidth=2.5, alpha=0.9, zorder=4)
    compress_left_line, = axis_map.plot([], [], color='#ff7f0e', linewidth=1.8, linestyle='--', alpha=0.9, zorder=4)
    compress_right_line, = axis_map.plot([], [], color='#2ca02c', linewidth=1.8, linestyle='--', alpha=0.9, zorder=4)
    left_marker, = axis_map.plot([], [], marker='o', color='#fb8500', markersize=9, zorder=5)
    right_marker, = axis_map.plot([], [], marker='o', color='#219ebc', markersize=9, zorder=5)
    midpoint_marker, = axis_map.plot([], [], marker='X', color='#d62728', markersize=10, zorder=6)

    info_box = axis_map.text(
        0.02,
        0.98,
        '',
        transform=axis_map.transAxes,
        va='top',
        ha='left',
        fontsize=9,
        bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': 0.75}
    )

    didactic_box = axis_state.text(
        0.02,
        0.98,
        '',
        transform=axis_state.transAxes,
        va='top',
        ha='left',
        fontsize=9,
        bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': 0.75}
    )

    phase_names = ['Selection', 'Compression', 'Fusion']
    phase_explanations = {
        'Selection': 'Model picks the best candidate pair from current star conditions.',
        'Compression': 'Pair approaches fusion site and overcomes the barrier.',
        'Fusion': 'Nuclei merge, element count drops, and core state is updated.',
    }
    frames_per_event = 3

    def _update(frame_index):
        event_index = frame_index // frames_per_event
        phase_index = frame_index % frames_per_event
        phase_name = phase_names[phase_index]
        event = fusion_events[event_index]
        left_x, left_y = event['left_pos']
        right_x, right_y = event['right_pos']
        mid_x, mid_y = event['midpoint']

        if phase_name == 'Selection':
            current_pair_line.set_data([left_x, right_x], [left_y, right_y])
            compress_left_line.set_data([], [])
            compress_right_line.set_data([], [])
            midpoint_marker.set_data([], [])
        elif phase_name == 'Compression':
            current_pair_line.set_data([], [])
            compress_left_line.set_data([left_x, mid_x], [left_y, mid_y])
            compress_right_line.set_data([right_x, mid_x], [right_y, mid_y])
            midpoint_marker.set_data([mid_x], [mid_y])
        else:
            current_pair_line.set_data([], [])
            compress_left_line.set_data([], [])
            compress_right_line.set_data([], [])
            midpoint_marker.set_data([mid_x], [mid_y])

        left_marker.set_data([left_x], [left_y])
        right_marker.set_data([right_x], [right_y])

        completed_events = event_index + 1 if phase_name == 'Fusion' else event_index
        completed_events = max(0, min(completed_events, len(fusion_events)))

        fused_node_ids = set()
        for ii in range(completed_events):
            fused_node_ids.add(_normalize_node_id(fusion_events[ii]['left_id']))
            fused_node_ids.add(_normalize_node_id(fusion_events[ii]['right_id']))

        fused_original = [
            points_by_node[node_id]
            for node_id in points_by_node
            if node_id in fused_node_ids
        ]
        active_original = [
            points_by_node[node_id]
            for node_id in points_by_node
            if node_id not in fused_node_ids
        ]

        active_original_points.set_data(
            [point[0] for point in active_original],
            [point[1] for point in active_original],
        )
        fused_original_points.set_data(
            [point[0] for point in fused_original],
            [point[1] for point in fused_original],
        )

        if completed_events > 0:
            fused_midpoints = [fusion_events[ii]['midpoint'] for ii in range(completed_events)]
            new_elements_points.set_data(
                [point[0] for point in fused_midpoints],
                [point[1] for point in fused_midpoints],
            )
            current_new_element.set_data([fused_midpoints[-1][0]], [fused_midpoints[-1][1]])
        else:
            new_elements_points.set_data([], [])
            current_new_element.set_data([], [])

        current_steps = steps[:completed_events]
        line_temp.set_data(current_steps, temperatures[:completed_events])
        line_pressure.set_data(current_steps, pressures[:completed_events])
        line_density.set_data(current_steps, densities[:completed_events])
        if current_steps:
            marker_temp.set_data([current_steps[-1]], [temperatures[completed_events - 1]])
            marker_pressure.set_data([current_steps[-1]], [pressures[completed_events - 1]])
            marker_density.set_data([current_steps[-1]], [densities[completed_events - 1]])
        else:
            marker_temp.set_data([], [])
            marker_pressure.set_data([], [])
            marker_density.set_data([], [])

        # Element type panel
        line_h.set_data(current_steps, h_counts[:completed_events])
        line_he.set_data(current_steps, he_counts[:completed_events])
        line_c.set_data(current_steps, c_counts[:completed_events])
        if current_steps:
            marker_h.set_data([current_steps[-1]],  [h_counts[completed_events - 1]])
            marker_he.set_data([current_steps[-1]], [he_counts[completed_events - 1]])
            marker_c.set_data([current_steps[-1]],  [c_counts[completed_events - 1]])
        else:
            marker_h.set_data([], [])
            marker_he.set_data([], [])
            marker_c.set_data([], [])
        if completed_events > 0:
            ev = fusion_events[completed_events - 1]
            tc = ev['type_counts']
            type_didactic.set_text(
                f"H: {tc.get('HIDROGEN', 0)}  "
                f"He: {tc.get('HELIUM', 0)}  "
                f"C: {tc.get('CARBON', 0)}"
            )
        else:
            type_didactic.set_text('')

        forced_label = 'yes' if event.get('forced') else 'no'
        info_box.set_text(
            f"phase: {phase_name}\n"
            f"step: {event['step']}\n"
            f"pair: {event['left_id']} + {event['right_id']}\n"
            f"score: {event['score']:.3f}\n"
            f"probability: {event['probability']:.3f}\n"
            f"forced: {forced_label}"
        )
        didactic_box.set_text(
            f"What to watch:\n"
            f"{phase_explanations[phase_name]}\n"
            f"\n"
            f"Completed fusions: {completed_events}/{len(fusion_events)}\n"
            f"Gray nodes are already fusionated; pink nodes are new fused elements."
        )

        return (
            active_original_points,
            fused_original_points,
            new_elements_points,
            current_new_element,
            current_pair_line,
            compress_left_line,
            compress_right_line,
            left_marker,
            right_marker,
            midpoint_marker,
            line_temp,
            line_pressure,
            line_density,
            marker_temp,
            marker_pressure,
            marker_density,
            info_box,
            didactic_box,
            line_h,
            line_he,
            line_c,
            marker_h,
            marker_he,
            marker_c,
            type_didactic,
        )

    animation = FuncAnimation(
        figure,
        _update,
        frames=len(fusion_events) * frames_per_event,
        interval=int(delay_seconds * 1000),
        blit=False,
        repeat=False,
    )

    # Keep a strong reference alive until rendering/saving finishes.
    figure._afn_animation = animation

    active_backend = plt.get_backend().lower()
    is_non_interactive = active_backend.endswith('agg')
    effective_record_file = record_file
    if is_non_interactive and effective_record_file is None:
        effective_record_file = 'educative_fusion.gif'
        print(
            'Non-interactive matplotlib backend detected '
            f'({plt.get_backend()}). Recording animation to {effective_record_file}.'
        )

    if effective_record_file:
        try:
            animation.save(effective_record_file)
        except Exception as error:
            raise RuntimeError(
                'Failed to record educational animation. '
                'Use .gif (requires Pillow) or .mp4 (requires ffmpeg).'
            ) from error

    if is_non_interactive:
        plt.close(figure)
        return effective_record_file

    figure.tight_layout()
    plt.show(block=True)
    return effective_record_file