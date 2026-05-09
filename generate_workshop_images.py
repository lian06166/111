"""
生成流水车间（Flow Shop）和作业车间（Job Shop）生产流程仿真对比图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

# ── 公共配置 ──────────────────────────────────────────────────────────────────
COLORS = {
    'machine': '#4A90D9',
    'job1': '#E74C3C',
    'job2': '#2ECC71',
    'job3': '#F39C12',
    'job4': '#9B59B6',
    'arrow': '#555555',
    'bg': '#F8F9FA',
    'title_bg': '#2C3E50',
    'grid': '#E0E0E0',
}

MACHINE_LABELS = ['机器 M1\n(工序1)', '机器 M2\n(工序2)', '机器 M3\n(工序3)', '机器 M4\n(工序4)']
JOB_LABELS = ['工件 J1', '工件 J2', '工件 J3', '工件 J4']


def draw_machine(ax, x, y, w, h, label, color='#4A90D9'):
    """绘制机器方框"""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor='white',
                         linewidth=2, zorder=3)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, label,
            ha='center', va='center', fontsize=11, fontweight='bold',
            color='white', zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, color='#555555', lw=2.0, style='->', label=None):
    """绘制箭头"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle='arc3,rad=0'))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.08, label, ha='center', va='bottom',
                fontsize=8, color=color)


# ══════════════════════════════════════════════════════════════════════════════
# 图1：流水车间（Flow Shop）—— 甘特图 + 流程示意
# ══════════════════════════════════════════════════════════════════════════════
def draw_flow_shop():
    fig = plt.figure(figsize=(16, 10), facecolor=COLORS['bg'])
    fig.suptitle('流水车间（Flow Shop）生产流程仿真',
                 fontsize=18, fontweight='bold', color='white',
                 bbox=dict(facecolor=COLORS['title_bg'], edgecolor='none',
                           boxstyle='round,pad=0.4'), y=0.97)

    # ── 左图：流程示意 ──────────────────────────────────────────────────────
    ax1 = fig.add_axes([0.03, 0.12, 0.42, 0.78])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_facecolor(COLORS['bg'])
    ax1.set_title('生产流程示意图', fontsize=13, fontweight='bold', pad=10)

    n_machines = 4
    machine_xs = [1.2, 3.5, 5.8, 8.1]
    machine_y = 6.5
    mw, mh = 1.8, 1.2

    # 画机器
    for i, (mx, ml) in enumerate(zip(machine_xs, MACHINE_LABELS)):
        draw_machine(ax1, mx, machine_y, mw, mh, ml, color=COLORS['machine'])

    # 机器间连线（主流向）
    for i in range(n_machines - 1):
        x1 = machine_xs[i] + mw
        x2 = machine_xs[i + 1]
        y = machine_y + mh / 2
        draw_arrow(ax1, x1, y, x2, y, color=COLORS['arrow'], lw=2.5)

    # 画工件（流水线同向）
    job_colors = [COLORS['job1'], COLORS['job2'], COLORS['job3'], COLORS['job4']]
    job_ys = [5.1, 3.8, 2.5, 1.2]
    for j, (jc, jy, jl) in enumerate(zip(job_colors, job_ys, JOB_LABELS)):
        # 起点标签
        ax1.text(0.1, jy + 0.3, jl, fontsize=10, fontweight='bold',
                 color=jc, va='center')
        # 依次经过每台机器
        for i, mx in enumerate(machine_xs):
            rect = FancyBboxPatch((mx + 0.2, jy), mw - 0.4, 0.6,
                                  boxstyle="round,pad=0.04",
                                  facecolor=jc, edgecolor='white',
                                  linewidth=1.5, alpha=0.85, zorder=3)
            ax1.add_patch(rect)
            ax1.text(mx + mw / 2, jy + 0.3, f'加工', ha='center',
                     va='center', fontsize=8, color='white', zorder=4)
            if i < n_machines - 1:
                draw_arrow(ax1, mx + mw - 0.2, jy + 0.3,
                           machine_xs[i + 1] + 0.2, jy + 0.3,
                           color=jc, lw=1.5)
        # 终点箭头
        ax1.annotate('', xy=(9.8, jy + 0.3), xytext=(machine_xs[-1] + mw - 0.1, jy + 0.3),
                     arrowprops=dict(arrowstyle='->', color=jc, lw=1.5))

    ax1.text(5.0, 0.4,
             '>> 所有工件按相同顺序 M1→M2→M3→M4 依次加工',
             ha='center', va='center', fontsize=9.5,
             color=COLORS['title_bg'],
             bbox=dict(facecolor='#DDE8F5', edgecolor=COLORS['machine'],
                       boxstyle='round,pad=0.3'))

    # ── 右图：甘特图 ──────────────────────────────────────────────────────────
    ax2 = fig.add_axes([0.52, 0.12, 0.45, 0.78])
    ax2.set_facecolor(COLORS['bg'])
    ax2.set_title('甘特图（Gantt Chart）', fontsize=13, fontweight='bold', pad=10)

    # 简单流水调度（处理时间各异）
    proc = [
        [3, 2, 4, 2],   # J1
        [2, 3, 2, 3],   # J2
        [4, 2, 3, 2],   # J3
        [2, 4, 2, 4],   # J4
    ]
    n_jobs, n_mach = 4, 4
    start = [[0] * n_mach for _ in range(n_jobs)]

    # 计算开始时间（流水车间调度）
    for j in range(n_jobs):
        for m in range(n_mach):
            if j == 0 and m == 0:
                start[j][m] = 0
            elif j == 0:
                start[j][m] = start[j][m - 1] + proc[j][m - 1]
            elif m == 0:
                start[j][m] = start[j - 1][m] + proc[j - 1][m]
            else:
                start[j][m] = max(start[j][m - 1] + proc[j][m - 1],
                                  start[j - 1][m] + proc[j - 1][m])

    yticks = list(range(n_mach))
    ylabels = [f'机器 M{m + 1}' for m in range(n_mach)]

    for m in range(n_mach):
        for j in range(n_jobs):
            s = start[j][m]
            p = proc[j][m]
            ax2.barh(m, p, left=s, height=0.55,
                     color=job_colors[j], edgecolor='white', linewidth=1.5,
                     alpha=0.9, label=JOB_LABELS[j] if m == 0 else '')
            ax2.text(s + p / 2, m, f'J{j + 1}', ha='center', va='center',
                     fontsize=9, fontweight='bold', color='white')

    max_time = max(start[j][n_mach - 1] + proc[j][n_mach - 1] for j in range(n_jobs))
    ax2.set_xlim(0, max_time + 1)
    ax2.set_ylim(-0.5, n_mach - 0.5)
    ax2.set_yticks(yticks)
    ax2.set_yticklabels(ylabels, fontsize=10)
    ax2.set_xlabel('时间（Time Units）', fontsize=10)
    ax2.grid(axis='x', color=COLORS['grid'], linestyle='--', alpha=0.7)
    ax2.spines[['top', 'right']].set_visible(False)

    handles = [mpatches.Patch(color=job_colors[j], label=JOB_LABELS[j])
               for j in range(n_jobs)]
    ax2.legend(handles=handles, loc='lower right', fontsize=9, framealpha=0.8)
    ax2.text(max_time / 2, -0.45,
             f'Makespan（完工时间）= {max_time} 时间单位',
             ha='center', va='center', fontsize=9,
             color=COLORS['title_bg'],
             bbox=dict(facecolor='#DDE8F5', edgecolor=COLORS['machine'],
                       boxstyle='round,pad=0.25'))

    plt.savefig('/home/runner/work/111/111/flow_shop_simulation.png',
                dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print('✅ flow_shop_simulation.png 已保存')


# ══════════════════════════════════════════════════════════════════════════════
# 图2：作业车间（Job Shop）—— 甘特图 + 流程示意
# ══════════════════════════════════════════════════════════════════════════════
def draw_job_shop():
    fig = plt.figure(figsize=(16, 10), facecolor=COLORS['bg'])
    fig.suptitle('作业车间（Job Shop）生产流程仿真',
                 fontsize=18, fontweight='bold', color='white',
                 bbox=dict(facecolor='#8E44AD', edgecolor='none',
                           boxstyle='round,pad=0.4'), y=0.97)

    # ── 左图：流程示意 ──────────────────────────────────────────────────────
    ax1 = fig.add_axes([0.03, 0.12, 0.42, 0.78])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_facecolor(COLORS['bg'])
    ax1.set_title('生产流程示意图', fontsize=13, fontweight='bold', pad=10)

    # 机器布局（2×2 网格）
    mpos = {
        'M1': (1.0, 6.8),
        'M2': (5.2, 6.8),
        'M3': (1.0, 3.5),
        'M4': (5.2, 3.5),
    }
    mlabels = {'M1': '机器 M1', 'M2': '机器 M2',
               'M3': '机器 M3', 'M4': '机器 M4'}
    mw, mh = 2.5, 1.2

    for key, (mx, my) in mpos.items():
        draw_machine(ax1, mx, my, mw, mh, mlabels[key], color=COLORS['machine'])

    # 每个工件不同加工路径
    routes = {
        'J1': ['M1', 'M3', 'M2', 'M4'],
        'J2': ['M2', 'M1', 'M4', 'M3'],
        'J3': ['M3', 'M4', 'M1', 'M2'],
        'J4': ['M4', 'M2', 'M3', 'M1'],
    }
    job_colors = [COLORS['job1'], COLORS['job2'], COLORS['job3'], COLORS['job4']]
    offsets = [0.25, 0.45, 0.65, 0.85]   # 箭头在机器框内的Y偏移

    for ji, (jname, route) in enumerate(routes.items()):
        jc = job_colors[ji]
        off = offsets[ji]
        ax1.text(0.05, 9.2 - ji * 0.55, f'● {jname}: {" → ".join(route)}',
                 fontsize=9, color=jc, fontweight='bold')
        for si in range(len(route) - 1):
            m_from = route[si]
            m_to = route[si + 1]
            fx, fy = mpos[m_from]
            tx, ty = mpos[m_to]
            # 从机器中心出发
            x1 = fx + mw / 2
            y1 = fy + mh * off
            x2 = tx + mw / 2
            y2 = ty + mh * off
            rad = 0.15 * ((-1) ** ji)
            ax1.annotate('', xy=(x2, y2), xytext=(x1, y1),
                         arrowprops=dict(arrowstyle='->', color=jc, lw=1.8,
                                         connectionstyle=f'arc3,rad={rad}'),
                         zorder=5)

    ax1.text(4.5, 0.4,
             '>> 每个工件拥有独立的加工路径，机器可被不同工件共享',
             ha='center', va='center', fontsize=9,
             color='#5D4037',
             bbox=dict(facecolor='#F3E5F5', edgecolor='#8E44AD',
                       boxstyle='round,pad=0.3'))

    # ── 右图：甘特图 ──────────────────────────────────────────────────────────
    ax2 = fig.add_axes([0.52, 0.12, 0.45, 0.78])
    ax2.set_facecolor(COLORS['bg'])
    ax2.set_title('甘特图（Gantt Chart）', fontsize=13, fontweight='bold', pad=10)

    # 作业车间调度数据（加工顺序 & 时间）
    jobs_data = {
        'J1': [('M1', 3), ('M3', 2), ('M2', 4), ('M4', 2)],
        'J2': [('M2', 2), ('M1', 3), ('M4', 2), ('M3', 3)],
        'J3': [('M3', 4), ('M4', 2), ('M1', 3), ('M2', 2)],
        'J4': [('M4', 2), ('M2', 4), ('M3', 2), ('M1', 4)],
    }
    machine_order = ['M1', 'M2', 'M3', 'M4']
    m_idx = {m: i for i, m in enumerate(machine_order)}

    # 简单贪心调度
    machine_avail = {m: 0 for m in machine_order}
    job_avail = {j: 0 for j in jobs_data}
    schedule = []   # (machine, job, start, duration)

    op_ptr = {j: 0 for j in jobs_data}
    ops_remaining = sum(len(v) for v in jobs_data.values())

    while ops_remaining > 0:
        advanced = False
        for jname, ops in jobs_data.items():
            ptr = op_ptr[jname]
            if ptr >= len(ops):
                continue
            mname, dur = ops[ptr]
            s = max(machine_avail[mname], job_avail[jname])
            # 只在机器和工件都就绪时安排
            if s == max(machine_avail[mname], job_avail[jname]):
                schedule.append((mname, jname, s, dur))
                machine_avail[mname] = s + dur
                job_avail[jname] = s + dur
                op_ptr[jname] += 1
                ops_remaining -= 1
                advanced = True
        if not advanced:
            # 推进时间到最近可用时间
            next_t = min(
                machine_avail[ops[op_ptr[j]][0]]
                for j, ops in jobs_data.items()
                if op_ptr[j] < len(ops)
            )
            for jname, ops in jobs_data.items():
                if op_ptr[jname] < len(ops):
                    mname, dur = ops[op_ptr[jname]]
                    if machine_avail[mname] <= next_t:
                        s = max(machine_avail[mname], job_avail[jname])
                        schedule.append((mname, jname, s, dur))
                        machine_avail[mname] = s + dur
                        job_avail[jname] = s + dur
                        op_ptr[jname] += 1
                        ops_remaining -= 1

    jname_to_idx = {'J1': 0, 'J2': 1, 'J3': 2, 'J4': 3}
    for mname, jname, s, dur in schedule:
        mi = m_idx[mname]
        ji = jname_to_idx[jname]
        ax2.barh(mi, dur, left=s, height=0.55,
                 color=job_colors[ji], edgecolor='white', linewidth=1.5,
                 alpha=0.9)
        ax2.text(s + dur / 2, mi, jname, ha='center', va='center',
                 fontsize=9, fontweight='bold', color='white')

    max_time = max(s + d for _, _, s, d in schedule)
    ax2.set_xlim(0, max_time + 1)
    ax2.set_ylim(-0.5, 3.5)
    ax2.set_yticks([0, 1, 2, 3])
    ax2.set_yticklabels(['机器 M1', '机器 M2', '机器 M3', '机器 M4'], fontsize=10)
    ax2.set_xlabel('时间（Time Units）', fontsize=10)
    ax2.grid(axis='x', color=COLORS['grid'], linestyle='--', alpha=0.7)
    ax2.spines[['top', 'right']].set_visible(False)

    handles = [mpatches.Patch(color=job_colors[j], label=JOB_LABELS[j])
               for j in range(4)]
    ax2.legend(handles=handles, loc='lower right', fontsize=9, framealpha=0.8)
    ax2.text(max_time / 2, -0.45,
             f'Makespan（完工时间）= {max_time} 时间单位',
             ha='center', va='center', fontsize=9,
             color='#5D4037',
             bbox=dict(facecolor='#F3E5F5', edgecolor='#8E44AD',
                       boxstyle='round,pad=0.25'))

    plt.savefig('/home/runner/work/111/111/job_shop_simulation.png',
                dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print('✅ job_shop_simulation.png 已保存')


# ══════════════════════════════════════════════════════════════════════════════
# 图3：对比总览图
# ══════════════════════════════════════════════════════════════════════════════
def draw_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=COLORS['bg'])
    fig.suptitle('流水车间 vs 作业车间——生产流程对比',
                 fontsize=17, fontweight='bold', y=1.01,
                 color=COLORS['title_bg'])

    titles = ['流水车间（Flow Shop）', '作业车间（Job Shop）']
    desc = [
        '工件按固定顺序经过所有机器\n加工路径：M1 → M2 → M3 → M4\n（适合大批量、标准化产品）',
        '每个工件路径不同，机器共享\n加工路径各异（如 J1: M1→M3→M2→M4）\n（适合多品种、小批量生产）',
    ]
    title_colors = [COLORS['machine'], '#8E44AD']

    # 简单示意（3台机器，3个工件）
    for ax, title, dc, tc in zip(axes, titles, desc, title_colors):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        ax.set_facecolor(COLORS['bg'])
        ax.set_title(title, fontsize=14, fontweight='bold', color=tc, pad=8)

        mxs = [1.0, 4.5, 8.0]
        my = 5.5
        for i, mx in enumerate(mxs):
            draw_machine(ax, mx, my, 2.0, 1.1, f'M{i + 1}\n(工序{i + 1})', color=tc)

        job_colors3 = [COLORS['job1'], COLORS['job2'], COLORS['job3']]
        job_ys = [4.1, 2.9, 1.7]

        if ax is axes[0]:
            # 流水：全部同向
            for ji, (jc, jy) in enumerate(zip(job_colors3, job_ys)):
                ax.text(0.1, jy + 0.3, f'J{ji + 1}', fontsize=10,
                        fontweight='bold', color=jc, va='center')
                for i, mx in enumerate(mxs):
                    r = FancyBboxPatch((mx + 0.2, jy), 1.6, 0.55,
                                      boxstyle="round,pad=0.04",
                                      facecolor=jc, edgecolor='white',
                                      linewidth=1.5, alpha=0.85, zorder=3)
                    ax.add_patch(r)
                    ax.text(mx + 1.0, jy + 0.27, '加工', ha='center',
                            va='center', fontsize=8, color='white', zorder=4)
                    if i < 2:
                        draw_arrow(ax, mx + 2.0, jy + 0.27,
                                   mxs[i + 1] + 0.2, jy + 0.27, color=jc, lw=1.2)
                ax.annotate('', xy=(10.0, jy + 0.27),
                            xytext=(mxs[-1] + 2.0, jy + 0.27),
                            arrowprops=dict(arrowstyle='->', color=jc, lw=1.2))
        else:
            # 作业：不同路径（用弯箭头）
            routes3 = [
                [0, 1, 2],   # J1: M1→M2→M3
                [1, 0, 2],   # J2: M2→M1→M3
                [2, 0, 1],   # J3: M3→M1→M2
            ]
            rads = [0.15, -0.25, 0.3]
            for ji, (jc, route, rad) in enumerate(zip(job_colors3, routes3, rads)):
                oy = 0.55 * (ji + 1) / 4.0
                ax.text(0.1, 1.2 + ji * 0.5,
                        f'J{ji + 1}: ' + '→'.join([f'M{r + 1}' for r in route]),
                        fontsize=9, color=jc, fontweight='bold')
                for si in range(len(route) - 1):
                    x1 = mxs[route[si]] + 1.0
                    x2 = mxs[route[si + 1]] + 1.0
                    ax.annotate('', xy=(x2, my + 0.55 * oy + 0.1),
                                xytext=(x1, my + 0.55 * oy + 0.1),
                                arrowprops=dict(arrowstyle='->', color=jc, lw=1.8,
                                                connectionstyle=f'arc3,rad={rad}'),
                                zorder=5)

        # 说明文字
        ax.text(5.0, 0.5, dc, ha='center', va='center', fontsize=9.5,
                color='#333333',
                bbox=dict(facecolor='white', edgecolor=tc,
                          boxstyle='round,pad=0.4', linewidth=1.5))

    plt.tight_layout()
    plt.savefig('/home/runner/work/111/111/workshop_comparison.png',
                dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print('✅ workshop_comparison.png 已保存')


if __name__ == '__main__':
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'WenQuanYi Zen Hei',
                                        'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    draw_flow_shop()
    draw_job_shop()
    draw_comparison()
    print('\n所有图片已生成完毕！')
