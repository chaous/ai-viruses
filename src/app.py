# src/app.py
import argparse

from .feature_extractor import extract_features, build_text_report
from .gpt_detector import analyze_report


def main():
    parser = argparse.ArgumentParser(description="AI Security Lab: file analyzer (GPT-based)")
    parser.add_argument("path", help="Path to file to analyze")
    args = parser.parse_args()

    path = args.path
    print(f"[+] Analyzing: {path}\n")

    # Локальные признаки
    size, entropy = extract_features(path)
    print("[+] Local features:")
    print(f"    - size: {size} bytes")
    print(f"    - entropy: {entropy:.3f}\n")

    # Текстовый отчёт
    report = build_text_report(path)

    # GPT-анализ
    print("[+] Sending report to GPT...")
    result = analyze_report(report)

    gpt_score = float(result.get("risk_score", 0.5))
    explanation = result.get("explanation", "no explanation")

    print("\n[+] GPT Response:")
    print(f"    - risk_score: {gpt_score:.3f}")
    print(f"    - explanation: {explanation}")


if __name__ == "__main__":
    main()
