FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --upgrade pip poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-root

# Copy project
COPY . .

CMD ["poetry", "run", "python", "app/bot/bot.py"]
