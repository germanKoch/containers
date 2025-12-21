# Лабораторная работа №1 — Dockerfile

## Цель работы

Создать два Dockerfile — «плохой» и «хороший», продемонстрировать плохие практики и их исправления. Также необходимо описать:
- две плохие практики использования контейнеров,
- два случая, когда **не стоит** использовать контейнеры,
- обязательное использование `volume`.

---

## Структура проекта

```text
.
├── app/
│   ├── app.py
│   └── requirements.txt
├── Dockerfile.bad
├── Dockerfile.good
├── docker-compose.yml
├── README.md
├── .dockerignore
└── .gitignore
```

---

## Приложение

Простое Flask-приложение, запускающее веб-сервер на порту 5000.

### `app/app.py`

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello from Docker lab!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### `app/requirements.txt`

```text
flask==3.0.0
```

---

## Плохой Dockerfile (`Dockerfile.bad`)

```Dockerfile
FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-flask

WORKDIR /app
COPY . .

EXPOSE 5000
CMD ["python3", "app/app.py"]
```

### Плохие практики:

1. Используется `ubuntu:latest` — нестабильный и неоптимизированный образ.
2. Много `RUN`-слоёв — увеличивают размер образа.
3. Нет очистки `apt`-кеша.
4. Python-библиотеки ставятся через `apt`, а не `pip`.
5. `COPY . .` — копирует весь контекст, включая лишние файлы.
6. Запуск от root (по умолчанию).

---

## Хороший Dockerfile (`Dockerfile.good`)

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

VOLUME /app/data

EXPOSE 5000

CMD ["python", "app.py"]
```

### Улучшения:

1. Использован `python:3.11-slim` — лёгкий, стабильный образ.
2. Используется `pip` для установки Python-зависимостей.
3. Оптимизирован порядок `COPY` для использования кэша.
4. `--no-cache-dir` уменьшает размер образа.
5. Копируются только нужные файлы (`app/`).
6. Добавлена директива `VOLUME /app/data` для явного указания точки монтирования volume.

---

## Сборка и запуск

### Вариант 1: Использование docker-compose (рекомендуется)

```bash
# Сборка и запуск с volume
docker-compose up -d --build

# Остановка
docker-compose down
```

### Вариант 2: Использование docker run

```bash
# Сборка
docker build -f Dockerfile.bad -t lab1-bad .
docker build -f Dockerfile.good -t lab1-good .

# Запуск (обязательно с volume)
docker run -d -p 5000:5000 -v labdata:/app/data lab1-good

# Проверка работы
curl http://localhost:5000
```

**Важно:** Volume `labdata` монтируется в `/app/data` внутри контейнера для сохранения данных между перезапусками контейнера.

---

## Плохие практики использования контейнеров

1. **Хранение секретов в Dockerfile или образе** — они легко извлекаются.
2. **Запуск от root без необходимости** — повышает риски безопасности.

---

## Когда НЕ стоит использовать контейнеры

1. **Программы с жёсткой привязкой к железу** (например, драйверы, low-latency-системы).
2. **Интенсивная работа с файловой системой** — контейнеры предполагают иммутабельность.

---

## Вывод

Описаны и реализованы два Dockerfile: плохой с намеренными ошибками и хороший с исправлениями. Проект построен на Flask-приложении, протестированы сценарии сборки и запуска. Добавлен volume, описаны антипаттерны и ограничения контейнеризации.
