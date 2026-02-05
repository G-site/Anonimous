# Anonim Message Bot

Telegram‑бот для анонимных сообщений между пользователями. Бот генерирует персональную ссылку, по которой друзьям можно отправлять анонимные сообщения, и поддерживает простой админ‑меню для рассылок.

## Возможности
- Персональная ссылка для анонимных сообщений (`/start`)
- Отправка сообщений любому пользователю бота (`/send`)
- FAQ и раздел “О нас” (`/instruction`, `/about`)
- Админ‑панель с рассылками (`/admin`)
- Платёж через Telegram Stars для функции “Узнать кто” (XTR)

## Требования
- Python 3.11+
- PostgreSQL
- Telegram Bot Token

## Установка
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Переменные окружения
Создайте `.env` в корне проекта:
```
TOKEN=your_telegram_bot_token
ADMIN=123456789

DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

HASHLIB_KEY=your_hash_salt
```

Дополнительно для скрипта синхронизации sequence:
```
DB_USERS_TABLE=users
DB_USERS_PRIMARY_ID_COLUMN=primary_id
```

## База данных
Проект ожидает таблицу `users` со следующими полями:
- `primary_id` (identity/auto‑increment)
- `id` (Telegram user id)
- `username`
- `name`
- `user_hash`
- `status` (например, `M` для админа)

Пример схемы:
```sql
CREATE TABLE users (
  primary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id BIGINT UNIQUE NOT NULL,
  username TEXT,
  name TEXT,
  user_hash TEXT,
  status TEXT DEFAULT NULL
);
```

## Запуск
```powershell
python main.py
```

## Админ‑команды
- `/admin` — открыть админ‑панель
- `/refund <user_id> <charge_id>` — возврат Telegram Stars

## Структура проекта
- `main.py` — запуск бота и регистрация роутеров
- `bot_instance.py` — создание `Bot` и `Dispatcher`
- `apps/handlers.py` — команды `/start`, `/about`, `/instruction`
- `apps/message.py` — отправка анонимных сообщений и оплата
- `apps/admin.py` — админ‑панель и рассылки
- `apps/database.py` — подключение к БД и запросы
