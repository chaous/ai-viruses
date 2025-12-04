FROM python:3.11-slim

# 1. Пакеты для анализа процессов/файлов
RUN apt-get update && apt-get install -y --no-install-recommends \
    strace \
    lsof \
    procps \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# 2. Создаём непривилегированного пользователя
RUN useradd -m appuser

WORKDIR /app

# 3. Зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Исходники
COPY src/ ./src

USER appuser

CMD ["python", "-m", "src.app"]
