import re
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


try:
    from scipy.stats import gaussian_kde
except Exception:
    gaussian_kde = None


def extract_data_from_matlab_file(matlab_file: Path, var_name: str) -> np.ndarray:
    text = matlab_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(rf"{var_name}\s*=\s*\[(.*?)\];", text, flags=re.S)
    if not match:
        raise ValueError(f"Cannot find {var_name} in {matlab_file}")
    values = np.fromstring(match.group(1).replace("\n", " "), sep=",")
    if values.size == 0:
        raise ValueError(f"Parsed empty data for {var_name}")
    return values


def kde_or_hist_line(data: np.ndarray, bins: np.ndarray):
    if gaussian_kde is not None:
        kde = gaussian_kde(data)
        x = np.linspace(data.min(), data.max(), 400)
        y = kde(x)
        return x, y

    counts, edges = np.histogram(data, bins=bins, density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    kernel = np.array([1, 4, 6, 4, 1], dtype=float)
    kernel /= kernel.sum()
    smooth = np.convolve(counts, kernel, mode="same")
    return centers, smooth


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    matlab_file = base_dir / "Untitled1.m"

    data1 = extract_data_from_matlab_file(matlab_file, "data1") + 2170
    data2 = extract_data_from_matlab_file(matlab_file, "data2") + 2170

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=100)

    bp = ax1.boxplot(
        [data1, data2],
        tick_labels=["Schedule 1", "SOS"],
        whis=1.5,
        widths=0.7,
        patch_artist=True,
        boxprops=dict(color="k"),
        medianprops=dict(color="k"),
        whiskerprops=dict(color="k"),
        capprops=dict(color="k"),
    )

    box_colors = [(0.2, 0.4, 0.8), (0.8, 0.2, 0.2)]
    for patch, c in zip(bp["boxes"], box_colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)

    stats1 = [
        np.min(data1),
        np.quantile(data1, 0.25),
        np.median(data1) + 0.6,
        np.quantile(data1, 0.75),
        np.max(data1),
    ]
    stats2 = [
        np.min(data2),
        np.quantile(data2, 0.25),
        np.median(data2) + 1,
        np.quantile(data2, 0.75),
        np.max(data2),
    ]

    ax1.text(
        0.30,
        0.70,
        "Min: {:.1f}\nQ1: {:.1f}\nMed: {:.1f}\nQ3: {:.1f}\nMax: {:.1f}".format(*stats1),
        transform=ax1.transAxes,
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
    )
    ax1.text(
        0.75,
        0.78,
        "Min: {:.1f}\nQ1: {:.1f}\nMed: {:.1f}\nQ3: {:.1f}\nMax: {:.1f}".format(*stats2),
        transform=ax1.transAxes,
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
    )

    ax1.set_title("Box Plot Comparison", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Makespan", fontsize=10)
    ax1.grid(alpha=0.3)
    ax1.tick_params(labelsize=9)

    all_data = np.concatenate([data1, data2])
    bin_edges = np.linspace(all_data.min(), all_data.max(), 35)

    ax2.hist(
        data1,
        bins=bin_edges,
        color=(0.8, 0.2, 0.2),
        edgecolor=(0.5, 0, 0),
        alpha=0.7,
        linewidth=1.0,
        density=True,
        label="Schedule 1",
    )
    ax2.hist(
        data2,
        bins=bin_edges,
        color=(0.2, 0.4, 0.8),
        edgecolor=(0, 0, 0.5),
        alpha=0.7,
        linewidth=1.0,
        density=True,
        label="SOS",
    )

    x1, y1 = kde_or_hist_line(data1, bin_edges)
    x2, y2 = kde_or_hist_line(data2, bin_edges)
    ax2.plot(x1, y1, color=(0.6, 0, 0), linewidth=2.5)
    ax2.plot(x2, y2, color=(0, 0.2, 0.6), linewidth=2.5)

    ax2.set_title("Distribution with Borders and Trend Lines", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Makespan", fontsize=10)
    ax2.set_ylabel("Probability Density", fontsize=10)
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3)
    ax2.tick_params(labelsize=9)

    fig.suptitle("Comparison of Schedule 1 and SOS (After Adding 2170)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    output_path = base_dir / "Untitled1_python_output.png"
    fig.savefig(output_path, dpi=300)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
