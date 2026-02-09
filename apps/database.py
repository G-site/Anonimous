import os
from hashids import Hashids
import asyncpg
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HASHLIB_KEY = os.getenv("HASHLIB_KEY")

hashids = Hashids(salt=HASHLIB_KEY, min_length=8)


pool: asyncpg.Pool | None = None


async def connect():
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            ssl="require"
        )
        print("Connected to DB")
    except Exception as e:
        print("Failed to connect to DB:", e)


async def set_user(id, username, name):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    encoded = hashids.encode(id)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT status FROM users WHERE id = $1;",
            id
        )
        if not row:
            await conn.execute(
                """
                INSERT INTO users (id, username, name, user_hash, created_at)
                VALUES ($1, $2, $3, $4, NOW());
                """,
                id, username, name, encoded
            )
        else:
            pass


async def check_admin(id):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT status FROM users WHERE id = $1;",
            id
        )
        return row["status"] if row else None


async def get_all_users():
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id FROM users;")
        return [row["id"] for row in rows]


async def get_my_hash(id):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT user_hash FROM users WHERE id = $1::bigint;", id)
        return row["user_hash"] if row else None


async def get_name_by_id(id):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT name FROM users WHERE id = $1;", id)
        return row["name"] if row else None
