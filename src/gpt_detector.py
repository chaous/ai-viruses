import os
import json
from typing import Dict, Any

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Ты аналитик по информационной безопасности.
Ты получаешь отчет о файле — только статические признаки (размер, энтропия, куски ASCII и т.п.).
Нужно:
- определить вероятность вредоносности от 0.0 до 1.0 (risk_score)
- кратко объяснить, почему такая оценка (explanation)

ВАЖНО:
- не подсказывать, как создавать, улучшать или обходить защиту.
- не давать примеров вредоносного кода.
Отвечай СТРОГО в формате JSON:

{
  "risk_score": <float>,
  "explanation": "<string>"
}
"""

def analyze_report(report: str) -> Dict[str, Any]:
    """
    Отправляет текстовый отчёт о файле в GPT и возвращает dict:
    {"risk_score": float, "explanation": str}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",           # можешь заменить на нужную модель
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Вот отчет о файле. Проанализируй его и верни JSON.\n\n"
                    + report
                ),
            },
        ],
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {
            "risk_score": 0.5,
            "explanation": "Не удалось корректно распарсить JSON ответа модели.",
        }

    # Гарантируем наличие полей
    if "risk_score" not in data:
        data["risk_score"] = 0.5
    if "explanation" not in data:
        data["explanation"] = "Модель не вернула explanation."

    return data
