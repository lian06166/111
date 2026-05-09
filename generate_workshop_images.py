"""生成3D流水车间与作业车间仿真对比图（机器使用具体图片贴图）"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ICON_PATHS = {
    'M1': '/home/runner/work/111/111/machine_M1.png',
    'M2': '/home/runner/work/111/111/machine_M2.png',
    'M3': '/home/runner/work/111/111/machine_M3.png',
    'M4': '/home/runner/work/111/111/machine_M4.png',
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
    """生成简易机器图标PNG（透明背景）"""
    h, w = 240, 240
    img = np.zeros((h, w, 4), dtype=float)

    # 机身
    img[60:200, 35:205, :3] = np.array(base_color)
    img[60:200, 35:205, 3] = 1.0

    # 高亮面
    img[72:125, 48:150, :3] = 0.85
    img[72:125, 48:150, 3] = 1.0

    # 面板
    img[135:187, 60:180, :3] = np.array([0.15, 0.2, 0.28])
    img[135:187, 60:180, 3] = 1.0

    # 指示灯
    img[145:160, 72:87, :3] = np.array([0.95, 0.2, 0.2])
    img[145:160, 72:87, 3] = 1.0
    img[145:160, 94:109, :3] = np.array([0.95, 0.8, 0.2])
    img[145:160, 94:109, 3] = 1.0
    img[145:160, 116:131, :3] = np.array([0.2, 0.85, 0.3])
    img[145:160, 116:131, 3] = 1.0

    # 传送带底座
    img[198:220, 22:218, :3] = np.array([0.22, 0.25, 0.3])
    img[198:220, 22:218, 3] = 1.0

    # 机器编号条
    img[20:50, 65:175, :3] = np.array([0.08, 0.12, 0.18])
    img[20:50, 65:175, 3] = 0.95

    plt.imsave(path, img)

    # 单独写编号，避免直接绘制数组文字复杂化
    fig = plt.figure(figsize=(2.4, 2.4), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img)
    ax.axis('off')
    ax.text(120, 35, machine_name, color='white', fontsize=16, fontweight='bold',
            ha='center', va='center')
    fig.savefig(path, transparent=True)
    plt.close(fig)


def create_machine_icons():
    color_map = {
        'M1': (0.32, 0.57, 0.86),
        'M2': (0.23, 0.68, 0.49),
        'M3': (0.95, 0.63, 0.17),
        'M4': (0.61, 0.35, 0.71),
    }
    for m, p in ICON_PATHS.items():
        create_machine_icon(p, color_map[m], m)


def add_icon_billboard(ax, icon, x, y, z, width=2.0, height=2.4):
    """在3D坐标中放置带贴图的机器图片平面"""
    if icon.dtype != float:
        icon = icon.astype(float) / 255.0
    ny, nx = icon.shape[0], icon.shape[1]

    u = np.linspace(-width / 2, width / 2, nx)
    v = np.linspace(0, height, ny)
    U, V = np.meshgrid(u, v)

    X = x + U
    Y = np.full_like(U, y)
    Z = z + V

    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=icon, shade=False, zorder=5)


def draw_floor(ax, xlim, ylim):
    xx = np.linspace(xlim[0], xlim[1], 20)
    yy = np.linspace(ylim[0], ylim[1], 20)
    X, Y = np.meshgrid(xx, yy)
    Z = np.zeros_like(X)
    ax.plot_surface(X, Y, Z, alpha=0.13, color='#7F8C8D', linewidth=0)


def draw_flow_shop_3d(machine_icons):
    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111, projection='3d')

    machine_pos = {'M1': (0, 0), 'M2': (4, 0), 'M3': (8, 0), 'M4': (12, 0)}

    draw_floor(ax, (-2, 14), (-3, 3))

    for m, (mx, my) in machine_pos.items():
        add_icon_billboard(ax, machine_icons[m], mx, my, 0)
        ax.text(mx, my, 2.75, m, ha='center', va='bottom', fontsize=10, fontweight='bold')

    routes = {
        'J1': ['M1', 'M2', 'M3', 'M4'],
        'J2': ['M1', 'M2', 'M3', 'M4'],
        'J3': ['M1', 'M2', 'M3', 'M4'],
        'J4': ['M1', 'M2', 'M3', 'M4'],
    }
    y_offsets = {'J1': -1.2, 'J2': -0.4, 'J3': 0.4, 'J4': 1.2}

    for j, route in routes.items():
        pts = np.array([[machine_pos[m][0], y_offsets[j], 0.65] for m in route])
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=JOB_COLORS[j], lw=3, marker='o', ms=5, label=j)
        for i in range(len(pts) - 1):
            d = pts[i + 1] - pts[i]
            ax.quiver(pts[i, 0], pts[i, 1], pts[i, 2], d[0], d[1], d[2],
                      color=JOB_COLORS[j], arrow_length_ratio=0.15, linewidth=2)

    ax.set_title('Flow Shop 3D Simulation (Same Route)', fontsize=14, fontweight='bold')
    ax.set_xlim(-2, 14)
    ax.set_ylim(-3, 3)
    ax.set_zlim(0, 3.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Height')
    ax.view_init(elev=26, azim=-59)
    ax.legend(loc='upper left')

    fig.savefig('/home/runner/work/111/111/flow_shop_3d_simulation.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    print('✅ flow_shop_3d_simulation.png 已保存')


def draw_job_shop_3d(machine_icons):
    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111, projection='3d')

    machine_pos = {'M1': (0, 0), 'M2': (6, 0), 'M3': (0, 4), 'M4': (6, 4)}

    draw_floor(ax, (-2, 8), (-2, 6))

    for m, (mx, my) in machine_pos.items():
        add_icon_billboard(ax, machine_icons[m], mx, my, 0)
        ax.text(mx, my, 2.75, m, ha='center', va='bottom', fontsize=10, fontweight='bold')

    routes = {
        'J1': ['M1', 'M3', 'M2', 'M4'],
        'J2': ['M2', 'M1', 'M4', 'M3'],
        'J3': ['M3', 'M4', 'M1', 'M2'],
        'J4': ['M4', 'M2', 'M3', 'M1'],
    }
    z_offsets = {'J1': 0.65, 'J2': 0.8, 'J3': 0.95, 'J4': 1.1}

    for j, route in routes.items():
        pts = np.array([[machine_pos[m][0], machine_pos[m][1], z_offsets[j]] for m in route])
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=JOB_COLORS[j], lw=3, marker='o', ms=5, label=j)
        for i in range(len(pts) - 1):
            d = pts[i + 1] - pts[i]
            ax.quiver(pts[i, 0], pts[i, 1], pts[i, 2], d[0], d[1], d[2],
                      color=JOB_COLORS[j], arrow_length_ratio=0.15, linewidth=2)

    ax.set_title('Job Shop 3D Simulation (Multiple Routes)', fontsize=14, fontweight='bold')
    ax.set_xlim(-2, 8)
    ax.set_ylim(-2, 6)
    ax.set_zlim(0, 3.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Height')
    ax.view_init(elev=28, azim=-48)
    ax.legend(loc='upper left')

    fig.savefig('/home/runner/work/111/111/job_shop_3d_simulation.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    print('✅ job_shop_3d_simulation.png 已保存')


def draw_comparison_3d(machine_icons):
    fig = plt.figure(figsize=(18, 8))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    # 左侧：Flow Shop
    flow_pos = {'M1': (0, 0), 'M2': (4, 0), 'M3': (8, 0), 'M4': (12, 0)}
    draw_floor(ax1, (-2, 14), (-3, 3))
    for m, (mx, my) in flow_pos.items():
        add_icon_billboard(ax1, machine_icons[m], mx, my, 0)
    for j, y0 in {'J1': -0.9, 'J2': 0.0, 'J3': 0.9}.items():
        pts = np.array([[flow_pos[m][0], y0, 0.75] for m in ['M1', 'M2', 'M3', 'M4']])
        ax1.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=JOB_COLORS[j], lw=3)
    ax1.set_title('Flow Shop: Same Route')
    ax1.set_xlim(-2, 14)
    ax1.set_ylim(-3, 3)
    ax1.set_zlim(0, 3.2)
    ax1.view_init(elev=24, azim=-58)

    # 右侧：Job Shop
    job_pos = {'M1': (0, 0), 'M2': (6, 0), 'M3': (0, 4), 'M4': (6, 4)}
    draw_floor(ax2, (-2, 8), (-2, 6))
    for m, (mx, my) in job_pos.items():
        add_icon_billboard(ax2, machine_icons[m], mx, my, 0)
    route_demo = {
        'J1': ['M1', 'M3', 'M2', 'M4'],
        'J2': ['M2', 'M1', 'M4', 'M3'],
        'J3': ['M3', 'M4', 'M1', 'M2'],
    }
    for j, route in route_demo.items():
        pts = np.array([[job_pos[m][0], job_pos[m][1], 0.75] for m in route])
        ax2.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=JOB_COLORS[j], lw=3)
    ax2.set_title('Job Shop: Different Routes')
    ax2.set_xlim(-2, 8)
    ax2.set_ylim(-2, 6)
    ax2.set_zlim(0, 3.2)
    ax2.view_init(elev=26, azim=-45)

    for ax in [ax1, ax2]:
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Height')

    fig.suptitle('3D Workshop Difference Comparison (Machine Image Textures)', fontsize=16, fontweight='bold')
    fig.savefig('/home/runner/work/111/111/workshop_3d_comparison.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    print('✅ workshop_3d_comparison.png 已保存')


def main():
    configure_fonts()
    create_machine_icons()
    machine_icons = {m: plt.imread(p) for m, p in ICON_PATHS.items()}

    draw_flow_shop_3d(machine_icons)
    draw_job_shop_3d(machine_icons)
    draw_comparison_3d(machine_icons)
    print('所有3D仿真图片已生成完毕！')


if __name__ == '__main__':
    main()
