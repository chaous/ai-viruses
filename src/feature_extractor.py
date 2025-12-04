import os
import math
from typing import List, Tuple

from .strings_tools import extract_strings_from_file, extract_artifacts


def file_entropy(path: str) -> float:
    with open(path, "rb") as f:
        data = f.read()
    return entropy_from_bytes(data)


def entropy_from_bytes(data: bytes) -> float:
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def compute_entropy_profile(path: str, chunk_size: int = 1024) -> List[float]:
    """
    Делит файл на блоки по chunk_size байт и считает энтропию каждого блока.
    Возвращает список энтропий.
    """
    entropies: List[float] = []
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            entropies.append(entropy_from_bytes(chunk))
    return entropies


def extract_features(path: str) -> Tuple[int, float]:
    size = os.path.getsize(path)
    entropy = file_entropy(path)
    return size, entropy


def build_text_report(path: str) -> str:
    size = os.path.getsize(path)
    entropy = file_entropy(path)

    # Профиль энтропии (ограничим до первых N блоков для отчёта)
    chunk_size = 1024
    entropy_profile = compute_entropy_profile(path, chunk_size=chunk_size)
    max_blocks_in_report = 32
    entropy_profile_short = entropy_profile[:max_blocks_in_report]

    # Для превью байтов, как раньше
    try:
        with open(path, "rb") as f:
            data_preview = f.read(4096)
    except OSError:
        data_preview = b""

    ascii_preview = "".join(
        chr(b) if 32 <= b < 127 else "."
        for b in data_preview
    )

    # Извлекаем строки из всего файла
    strings = extract_strings_from_file(path, min_len=5)
    max_strings_in_report = 30
    strings_for_report = strings[:max_strings_in_report]

    artifacts = extract_artifacts(strings)
    urls = artifacts["urls"][:10]
    emails = artifacts["emails"][:10]
    ips = artifacts["ips"][:10]
    paths = artifacts["paths"][:10]

    # Формируем текстовый отчёт (то, что уйдёт в GPT)
    report_lines = []

    report_lines.append(f"Путь: {path}")
    report_lines.append(f"Размер (байты): {size}")
    report_lines.append(f"Энтропия (общая): {entropy:.3f}")
    report_lines.append("")
    report_lines.append("Профиль энтропии по блокам (chunk_size = 1024 байт):")
    for i, e in enumerate(entropy_profile_short):
        offset = i * chunk_size
        report_lines.append(f"  Блок {i:03d} (смещение {offset}): энтропия = {e:.3f}")
    if len(entropy_profile) > max_blocks_in_report:
        report_lines.append(
            f"  ... ещё {len(entropy_profile) - max_blocks_in_report} блок(ов) скрыто в отчёте."
        )

    report_lines.append("")
    report_lines.append("ASCII-представление первых 4096 байт:")
    report_lines.append(ascii_preview)
    report_lines.append("")

    report_lines.append("Извлечённые строки (первые {0}):".format(len(strings_for_report)))
    for s in strings_for_report:
        report_lines.append(f"  {s}")
    if len(strings) > max_strings_in_report:
        report_lines.append(
            f"  ... ещё {len(strings) - max_strings_in_report} строк скрыто в отчёте."
        )

    report_lines.append("")
    report_lines.append("Найденные артефакты:")
    report_lines.append(f"  URL (до 10): {urls if urls else 'нет'}")
    report_lines.append(f"  Email (до 10): {emails if emails else 'нет'}")
    report_lines.append(f"  IP-адреса (до 10): {ips if ips else 'нет'}")
    report_lines.append(f"  Пути к файлам (до 10): {paths if paths else 'нет'}")

    return "\n".join(report_lines)
