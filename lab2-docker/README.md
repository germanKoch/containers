## ЛР 2. Docker Compose

В этой директории находится compose‑проект для Flask‑приложения из ЛР1 и базы данных PostgreSQL.

### Сервисы

- **web**  
  - Flask‑приложение, собирается из локального `Dockerfile.good` (`build.context: .`, `dockerfile: Dockerfile.good`).  
  - Образ получает имя `lab2_flask_app` через ключ `image`.  
  - Контейнер имеет жёсткое имя `lab2_web`.  
  - Порт 5000 приложения проброшен наружу как `${WEB_PORT}:5000` (значение задаётся в `.env`).  
  - Использует общую сеть `lab2_net`.  
  - Имеет `depends_on: - db`.  
  - Имеет `command: ["python", "app.py"]`, что переиспользует команду из Dockerfile.  
  - Содержит `healthcheck`, который с помощью Python‑скрипта опрашивает `http://localhost:5000/`.

- **db**  
  - Контейнер PostgreSQL на образе `postgres:16` с жёстким именем `lab2_db`.  
  - Переменные окружения (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) берутся из файла `.env` через `env_file`.  
  - Использует именованный volume `db_data:/var/lib/postgresql/data` для сохранения данных.  
  - Подключен к сети `lab2_net`.  
  - Имеет `healthcheck` c использованием `pg_isready`.

- **init-db** (одноразовый init‑сервис)  
  - Базируется на образе `postgres:16`, контейнер `lab2_init_db`.  
  - Использует те же переменные окружения БД через `env_file: .env`.  
  - Имеет `depends_on` с условием `service_healthy` от сервиса `db`, чтобы запускаться только после готовности БД.  
  - Выполняет команду `psql`, создающую таблицу `items` в базе (`CREATE TABLE IF NOT EXISTS items (...)`).  
  - Подключён к сети `lab2_net`.  
  - `restart: "no"`, то есть отрабатывает один раз как init‑контейнер.

### Сеть и volume

- **Сеть**:  
  - Явно объявлена пользовательская сеть `lab2_net` с драйвером `bridge`.  
  - Все три сервиса (`web`, `db`, `init-db`) подключены к этой сети.

- **Volume**:  
  - Именованный volume `db_data` используется сервисом `db` для хранения данных PostgreSQL.

### Переменные окружения

- Все переменные окружения должны быть вынесены из `docker-compose.yml` в файл `.env` рядом с ним (файл нужно создать самостоятельно).  
- В `.env` задаются, как минимум:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
  - `WEB_PORT` — внешний порт, на который пробрасывается порт 5000 контейнера `web`.

Пример содержимого `.env`:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=lab2db

WEB_PORT=5000
```

### Запуск

- **Полный запуск всех сервисов**:

```bash
docker compose up --build
```

или (в фоне):

```bash
docker compose up --build -d
```

- Приложение будет доступно по адресу `http://localhost:${WEB_PORT}` (по умолчанию `http://localhost:5000`).

### Ответы на вопросы

1. **Можно ли ограничивать ресурсы (например, память или CPU) для сервисов в docker-compose.yml? Если нет, то почему, если да, то как?**  
   Да, можно, но способ зависит от сценария использования:
   - Для режима Swarm (`docker stack deploy`) ограничения ресурсов задаются через секцию `deploy.resources`:
     ```yaml
     services:
       web:
         deploy:
           resources:
             limits:
               cpus: "0.5"
               memory: "512M"
             reservations:
               cpus: "0.25"
               memory: "256M"
     ```
     Эти параметры реально учитываются только при запуске через Swarm (docker stack).
   - При использовании классического `docker-compose up` секция `deploy` игнорируется, но можно использовать опции прошлого формата (версии 2, такие как `mem_limit`, `cpus` и т.п.), либо задавать лимиты напрямую через `docker run`. В актуальной практике, если нужны гарантированные лимиты именно из compose‑файла, обычно переходят на Swarm и `deploy.resources`.

2. **Как можно запустить только определенный сервис из docker-compose.yml, не запуская остальные?**  
   Достаточно указать имя сервиса в команде:
   - Запуск только веб‑сервиса:
     ```bash
     docker compose up web
     ```
   - Аналогично можно запускать любой другой сервис:
     ```bash
     docker compose up db
     ```
   Опционально можно добавить флаг `-d` для фонового запуска. Если сервис зависит от других (`depends_on`), docker сам поднимет необходимые зависимые сервисы.


