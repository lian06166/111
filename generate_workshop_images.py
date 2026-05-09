"""生成2D车间流程对比图：流水车间 vs 柔性作业车间（单张PNG）"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

BASE_DIR = '/home/runner/work/111/111'
OUTPUT_PATH = f'{BASE_DIR}/workshop_comparison.png'

ICON_PATHS = {
    'M1': f'{BASE_DIR}/machine_M1.png',
    'M2': f'{BASE_DIR}/machine_M2.png',
    'M3': f'{BASE_DIR}/machine_M3.png',
    'M4': f'{BASE_DIR}/machine_M4.png',
}

JOB_COLORS = {
    'J1': '#E74C3C',
    'J2': '#2ECC71',
    'J3': '#F39C12',
    'J4': '#9B59B6',
}


def configure_fonts():
    plt.rcParams['font.sans-serif'] = [
        'Noto Sans CJK JP', 'WenQuanYi Zen Hei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans'
    ]
    plt.rcParams['axes.unicode_minus'] = False


def create_machine_icon(path, base_color, machine_name):
    h, w = 220, 220
    img = np.zeros((h, w, 4), dtype=float)

    img[56:184, 32:188, :3] = np.array(base_color)
    img[56:184, 32:188, 3] = 1.0

    img[68:118, 44:138, :3] = 0.86
    img[68:118, 44:138, 3] = 1.0

    img[124:172, 56:166, :3] = np.array([0.14, 0.20, 0.28])
    img[124:172, 56:166, 3] = 1.0

    img[136:150, 68:82, :3] = np.array([0.95, 0.2, 0.2])
    img[136:150, 68:82, 3] = 1.0
    img[136:150, 89:103, :3] = np.array([0.95, 0.8, 0.2])
    img[136:150, 89:103, 3] = 1.0
    img[136:150, 110:124, :3] = np.array([0.2, 0.85, 0.3])
    img[136:150, 110:124, 3] = 1.0

    img[182:204, 20:200, :3] = np.array([0.22, 0.25, 0.3])
    img[182:204, 20:200, 3] = 1.0

    fig = plt.figure(figsize=(2.2, 2.2), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img)
    ax.axis('off')
    ax.text(110, 34, machine_name, color='white', fontsize=16, fontweight='bold', ha='center', va='center')
    fig.savefig(path, transparent=True)
    plt.close(fig)


def create_machine_icons():
    color_map = {
        'M1': (0.32, 0.57, 0.86),
        'M2': (0.23, 0.68, 0.49),
        'M3': (0.95, 0.63, 0.17),
        'M4': (0.61, 0.35, 0.71),
    }
    for machine, path in ICON_PATHS.items():
        create_machine_icon(path, color_map[machine], machine)


def add_machine_image(ax, machine_icons, machine, x, y, label):
    image = OffsetImage(machine_icons[machine], zoom=0.26)
    ab = AnnotationBbox(image, (x, y), frameon=False, box_alignment=(0.5, 0.5), zorder=4)
    ax.add_artist(ab)
    ax.text(x, y - 0.95, label, ha='center', va='top', fontsize=10, fontweight='bold', color='#2C3E50')


def draw_job_routes(ax, machine_positions, routes, job_y_jitter):
    for job, route in routes.items():
        color = JOB_COLORS[job]
        xs = [machine_positions[m][0] for m in route]
        ys = [machine_positions[m][1] + job_y_jitter[job] for m in route]
        ax.plot(xs, ys, color=color, lw=2.5, marker='o', ms=4, zorder=3)

        for i in range(len(xs) - 1):
            ax.annotate(
                '',
                xy=(xs[i + 1], ys[i + 1]),
                xytext=(xs[i], ys[i]),
                arrowprops=dict(arrowstyle='->', color=color, lw=2),
                zorder=3,
            )


def draw_flow_panel(ax, machine_icons):
    ax.set_title('Flow Shop', fontsize=13, fontweight='bold', color='#1F4E79')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor('#F7FAFD')

    machine_positions = {
        'M1': (2.2, 5.0),
        'M2': (6.0, 5.0),
        'M3': (9.8, 5.0),
        'M4': (13.6, 5.0),
    }

    for m, (x, y) in machine_positions.items():
        add_machine_image(ax, machine_icons, m, x, y, m)

    routes = {
        'J1': ['M1', 'M2', 'M3', 'M4'],
        'J2': ['M1', 'M2', 'M3', 'M4'],
        'J3': ['M1', 'M2', 'M3', 'M4'],
        'J4': ['M1', 'M2', 'M3', 'M4'],
    }
    y_jitter = {'J1': -1.2, 'J2': -0.6, 'J3': 0.0, 'J4': 0.6}
    draw_job_routes(ax, machine_positions, routes, y_jitter)

    ax.text(
        8.0,
        1.0,
        'All jobs share the same route: M1 → M2 → M3 → M4',
        ha='center',
        va='center',
        fontsize=9.5,
        bbox=dict(facecolor='white', edgecolor='#1F4E79', boxstyle='round,pad=0.3'),
    )


def draw_job_shop_panel(ax, machine_icons):
    ax.set_title('Flexible Job Shop', fontsize=13, fontweight='bold', color='#7A1F7A')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor('#FDF7FD')

    machine_positions = {
        'M1': (4.0, 6.2),
        'M2': (12.0, 6.2),
        'M3': (4.0, 3.2),
        'M4': (12.0, 3.2),
    }

    for m, (x, y) in machine_positions.items():
        add_machine_image(ax, machine_icons, m, x, y, m)

    routes = {
        'J1': ['M1', 'M3', 'M2', 'M4'],
        'J2': ['M2', 'M1', 'M4', 'M3'],
        'J3': ['M3', 'M4', 'M1', 'M2'],
        'J4': ['M4', 'M2', 'M3', 'M1'],
    }
    y_jitter = {'J1': 0.22, 'J2': 0.07, 'J3': -0.07, 'J4': -0.22}
    draw_job_routes(ax, machine_positions, routes, y_jitter)

    ax.text(
        8.0,
        1.0,
        'Each job follows a different route and shares machines dynamically',
        ha='center',
        va='center',
        fontsize=9.5,
        bbox=dict(facecolor='white', edgecolor='#7A1F7A', boxstyle='round,pad=0.3'),
    )


def draw_comparison(machine_icons):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), facecolor='white')

    draw_flow_panel(ax1, machine_icons)
    draw_job_shop_panel(ax2, machine_icons)

    legend_handles = [
        mpatches.Patch(color=JOB_COLORS['J1'], label='Job J1'),
        mpatches.Patch(color=JOB_COLORS['J2'], label='Job J2'),
        mpatches.Patch(color=JOB_COLORS['J3'], label='Job J3'),
        mpatches.Patch(color=JOB_COLORS['J4'], label='Job J4'),
    ]
    fig.legend(handles=legend_handles, loc='lower center', ncol=4, frameon=False, fontsize=10)

    fig.suptitle('Workshop Process Comparison (2D): Flow Shop vs Flexible Job Shop', fontsize=16, fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches='tight')
    plt.close(fig)
    print(f'✅ {OUTPUT_PATH} 已保存')


def main():
    configure_fonts()
    create_machine_icons()
    machine_icons = {m: plt.imread(p) for m, p in ICON_PATHS.items()}
    draw_comparison(machine_icons)
    print('2D comparison simulation image generated.')


if __name__ == '__main__':
    main()
