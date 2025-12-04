import re
from typing import List, Dict, Any


def extract_strings_from_bytes(data: bytes, min_len: int = 4) -> List[str]:
    """
    Извлекает печатаемые ASCII-строки из массива байт.
    Аналог утилиты `strings`.
    """
    result = []
    current = []

    for b in data:
        # Печатаемые ASCII-символы (можно подстроить под себя)
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                result.append("".join(current))
            current = []

    if len(current) >= min_len:
        result.append("".join(current))

    return result


def extract_strings_from_file(path: str, min_len: int = 4) -> List[str]:
    with open(path, "rb") as f:
        data = f.read()
    return extract_strings_from_bytes(data, min_len=min_len)


def extract_artifacts(strings: List[str]) -> Dict[str, Any]:
    """
    Ищем простые артефакты в строках:
    - URL
    - email
    - IP-адреса
    - пути к файлам (примитивно)
    """
    urls = set()
    emails = set()
    ips = set()
    paths = set()

    url_re = re.compile(r"https?://[^\s\"'>]+", re.IGNORECASE)
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    ip_re = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    path_re = re.compile(r"(?:[A-Za-z]:\\[^\s]+|/[^ \t\n\r\"']+)")

    for s in strings:
        for m in url_re.findall(s):
            urls.add(m)
        for m in email_re.findall(s):
            emails.add(m)
        for m in ip_re.findall(s):
            ips.add(m)
        for m in path_re.findall(s):
            paths.add(m)

    return {
        "urls": sorted(urls),
        "emails": sorted(emails),
        "ips": sorted(ips),
        "paths": sorted(paths),
    }
