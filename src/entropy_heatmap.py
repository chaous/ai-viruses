import argparse
import math
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from .feature_extractor import compute_entropy_profile


def build_entropy_grid(entropies, cols: int) -> np.ndarray:
    """
    Превращает 1D-список энтропий в 2D-сетку для тепловой карты.
    Пустые ячейки заполняются NaN.
    """
    n = len(entropies)
    if n == 0:
        return np.zeros((0, 0), dtype=float)

    rows = math.ceil(n / cols)
    grid = np.full((rows, cols), np.nan, dtype=float)

    for i, e in enumerate(entropies):
        r = i // cols
        c = i % cols
        grid[r, c] = e

    return grid


def main():
    parser = argparse.ArgumentParser(
        description="Entropy heatmap generator (PNG)."
    )
    parser.add_argument("path", help="Путь к файлу для анализа")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024,
        help="Размер блока в байтах (по умолчанию 1024)",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=0,
        help="Количество колонок в тепловой карте (0 = подобрать автоматически)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="entropy_heatmap.png",
        help="Путь к выходному PNG-файлу (по умолчанию entropy_heatmap.png)",
    )

    args = parser.parse_args()

    entropies = compute_entropy_profile(args.path, chunk_size=args.chunk_size)
    if not entropies:
        print("Файл пустой или не удалось прочитать.")
        return

    n_blocks = len(entropies)

    # Если cols не задан (0) — подбираем автоматически около sqrt(N)
    if args.cols <= 0:
        auto_cols = max(1, int(math.ceil(math.sqrt(n_blocks))))
        cols = auto_cols
    else:
        cols = args.cols

    grid = build_entropy_grid(entropies, cols=cols)

    # Маскируем NaN, чтобы пустые ячейки не портили вид
    grid_masked = np.ma.masked_invalid(grid)

    out_path = Path(args.output)
    if out_path.parent and not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots()
    im = ax.imshow(
        grid_masked,
        interpolation="nearest",
        aspect="auto",
        vmin=0.0,
        vmax=8.0,
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Entropy (bits per byte)")

    ax.set_title(f"Entropy heatmap: {args.path}")
    ax.set_xlabel("Block column")
    ax.set_ylabel("Row")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[+] Blocks: {n_blocks}, cols: {cols}")
    print(f"[+] Saved entropy heatmap to: {out_path}")


if __name__ == "__main__":
    main()
