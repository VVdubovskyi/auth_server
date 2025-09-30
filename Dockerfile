FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо залежності і встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту
COPY . .

# Точка входу для запуску FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
