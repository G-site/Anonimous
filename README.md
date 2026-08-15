# Anonim Message Bot

Telegram-бот для обмена анонимными сообщениями. После запуска пользователь получает персональную ссылку: открывший её человек может отправить получателю текст, фото, стикер или другое сообщение. Получатель может анонимно ответить либо раскрыть отправителя за Telegram Stars или с помощью промокода.

## Возможности

- персональная deep-link ссылка для анонимных сообщений;
- отправка сообщений по ссылке или через команду `/send`;
- анонимные ответы на полученные сообщения;
- раскрытие отправителя за 20 Telegram Stars (XTR) или по промокоду;
- профиль со статистикой отправленных, полученных и просмотренных сообщений;
- одноразовые, многоразовые и технические промокоды;
- админ-панель с рассылками и экспортом базы пользователей в Excel;
- еженедельное обновление технического промокода и публикация в Telegram-канале.

## Стек

- Python 3.11+
- [aiogram 3](https://docs.aiogram.dev/)
- PostgreSQL и `asyncpg`
- APScheduler

## Установка

```powershell
git clone git clone https://github.com/G-site/Anonimous.git
cd anonim-mess
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Настройка окружения

Создайте в корне проекта файл `.env`. Он уже исключён из Git и не должен публиковаться.

```env
# Токен, выданный BotFather
TOKEN=your_telegram_bot_token

# PostgreSQL
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Секретная соль для генерации персональных ссылок
HASHLIB_KEY=replace_with_a_long_random_secret
```

> Подключение к базе создаётся с `ssl="require"`; используйте PostgreSQL-хостинг с поддержкой SSL или скорректируйте настройку в `apps/database.py` для локальной базы.

`HASHLIB_KEY` нельзя менять после запуска в production: старые персональные ссылки перестанут корректно распознаваться.

## Подготовка базы данных

Создайте таблицы в PostgreSQL:

```sql
CREATE TABLE users (
    primary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id BIGINT UNIQUE NOT NULL,
    username TEXT,
    name TEXT,
    user_hash TEXT UNIQUE NOT NULL,
    status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent INTEGER NOT NULL DEFAULT 0,
    viewed INTEGER NOT NULL DEFAULT 0,
    wasted INTEGER NOT NULL DEFAULT 0,
    received INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE promocodes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    uses INTEGER NOT NULL
);

-- Нужен для функции «Получить тех. промокод» и еженедельного обновления.
INSERT INTO promocodes (code, type, uses)
VALUES ('INITIALTECH', 'tech', 999);
```

Чтобы дать пользователю доступ к админ-панели, укажите для него статус `M`:

```sql
UPDATE users SET status = 'M' WHERE id = <telegram_user_id>;
```

Для существующей базы со старой структурой используйте миграцию:

```powershell
python test\alter_users_table.py
```

## Запуск

```powershell
python main.py
```

Бот работает через long polling. Для остановки нажмите `Ctrl+C`.

## Команды

| Команда | Назначение |
| --- | --- |
| `/start` | открыть меню и получить персональную ссылку |
| `/profile` | посмотреть статистику профиля |
| `/send` | выбрать получателя и отправить анонимное сообщение |
| `/about` | информация о боте и ссылки на канал/поддержку |
| `/instruction` | FAQ |
| `/admin` | админ-панель (только пользователи со статусом `M`) |
| `/refund <user_id> <charge_id>` | вернуть платёж Telegram Stars (только администратор) |

## Админ-панель

Администратор может отправить всем пользователям уведомление о техническом перерыве, просьбу поделиться ботом или подписаться на канал, выгрузить таблицу `users` в `.xlsx`, а также создать промокоды:

- одноразовый — одно использование;
- многоразовый — до 99 использований;
- технический — единый для всех администраторов и обновляется по воскресеньям.

Параметры еженедельной задачи — чат, изображение и время запуска — находятся в `apps/sender.py`.

## Структура проекта

```text
.
├── main.py                   # запуск бота, роутеры и команды Telegram
├── bot_instance.py           # экземпляры Bot и Dispatcher
├── apps/
│   ├── handlers.py           # стартовое меню, профиль, FAQ и «О нас»
│   ├── message.py            # анонимные сообщения, Stars и промокоды
│   ├── admin.py              # админ-панель, рассылки, экспорт в Excel
│   ├── database.py           # пул PostgreSQL и запросы к БД
│   └── sender.py             # планировщик еженедельной задачи
├── test/alter_users_table.py # миграция счётчиков пользователей
└── requirements.txt
```

## Безопасность

Не добавляйте в репозиторий `.env`, токен бота, пароль PostgreSQL или `HASHLIB_KEY`. При компрометации токена отзовите его через BotFather и обновите значение в окружении.
