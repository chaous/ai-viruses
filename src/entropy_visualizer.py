import argparse

from .feature_extractor import compute_entropy_profile


def ascii_bar(value: float, max_value: float = 8.0, width: int = 40) -> str:
    """
    Рисует простую ASCII-бару по значению value (обычно энтропия 0..8).
    """
    ratio = max(0.0, min(1.0, value / max_value))
    filled = int(ratio * width)
    return "#" * filled + "." * (width - filled)


def main():
    parser = argparse.ArgumentParser(
        description="Entropy profile visualizer (per-chunk entropy)."
    )
    parser.add_argument("path", help="Путь к файлу")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024,
        help="Размер блока в байтах (по умолчанию 1024)",
    )
    args = parser.parse_args()

    entropies = compute_entropy_profile(args.path, chunk_size=args.chunk_size)

    if not entropies:
        print("Файл пустой или не удалось прочитать.")
        return

    print(f"Файл: {args.path}")
    print(f"Chunk size: {args.chunk_size} байт")
    print(f"Всего блоков: {len(entropies)}")
    print()

    for i, e in enumerate(entropies):
        bar = ascii_bar(e)
        print(f"{i:03d} | {e:5.2f} | {bar}")


if __name__ == "__main__":
    main()
