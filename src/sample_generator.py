import os
import argparse
import random


def generate_benign_text(path: str, size_kb: int = 4):
    text = (
        "This is a harmless sample file used for testing the AI security lab. "
        "It contains only readable ASCII text and no executable code.\n"
    )
    data = (text * ((size_kb * 1024) // len(text) + 1)).encode("utf-8")
    with open(path, "wb") as f:
        f.write(data[: size_kb * 1024])


def generate_suspicious_binary(path: str, size_kb: int = 4):
    size = size_kb * 1024
    data = os.urandom(size)
    with open(path, "wb") as f:
        f.write(data)


def generate_mixed_sample(path: str, chunk_kb: int = 4):
    """
    Файл из нескольких разных по структуре сегментов:
    - нули (очень низкая энтропия)
    - повторяющийся ASCII-текст (низкая/средняя)
    - случайные байты (высокая)
    - простой паттерн (ABCD1234...) (средняя)
    """
    parts = []

    # 1) нули
    parts.append(b"\x00" * (chunk_kb * 1024))

    # 2) повторяющийся текст
    text = (
        "This is benign repeating text block used for mixed entropy sample. "
    ).encode("utf-8")
    text_block = (text * ((chunk_kb * 1024) // len(text) + 1))[: chunk_kb * 1024]
    parts.append(text_block)

    # 3) случайные байты
    parts.append(os.urandom(chunk_kb * 1024))

    # 4) простой паттерн
    pattern = (b"ABCD1234" * ((chunk_kb * 1024) // 8 + 1))[: chunk_kb * 1024]
    parts.append(pattern)

    with open(path, "wb") as f:
        for p in parts:
            f.write(p)


def main():
    parser = argparse.ArgumentParser(description="Synthetic sample generator (SAFE)")
    parser.add_argument("path", help="Output file path")
    parser.add_argument(
        "--type",
        choices=["benign", "suspicious", "mixed"],
        default="benign",
        help="Type of sample to generate",
    )
    parser.add_argument(
        "--size-kb",
        type=int,
        default=8,
        help="Approx size of file in kilobytes (для benign/suspicious)",
    )
    parser.add_argument(
        "--chunk-kb",
        type=int,
        default=4,
        help="Размер одного сегмента для mixed (по умолчанию 4 KB)",
    )

    args = parser.parse_args()

    if args.type == "benign":
        generate_benign_text(args.path, args.size_kb)
        print(f"[+] Generated benign sample: {args.path}")
    elif args.type == "suspicious":
        generate_suspicious_binary(args.path, args.size_kb)
        print(f"[+] Generated suspicious-looking binary sample: {args.path}")
    else:  # mixed
        generate_mixed_sample(args.path, args.chunk_kb)
        print(f"[+] Generated mixed-entropy sample: {args.path}")


if __name__ == "__main__":
    main()
