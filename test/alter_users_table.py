import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("DB_HOST")
PG_PORT = os.getenv("DB_PORT", 5432)  # по умолчанию 5432
PG_USER = os.getenv("DB_USER")
PG_PASSWORD = os.getenv("DB_PASSWORD")
PG_DB = os.getenv("DB_NAME")


async def migrate():
    conn = await asyncpg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DB
    )

    try:
        # Удаляем старые колонки
        await conn.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS messages_sent,
        DROP COLUMN IF EXISTS recognized;
        """)

        # Добавляем новые колонки с дефолтным 0
        await conn.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS sent INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS viewed INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS wasted INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS received INTEGER DEFAULT 0;
        """)

        print("✅ Миграция выполнена успешно")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate())