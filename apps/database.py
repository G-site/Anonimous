import os
from hashids import Hashids
import psycopg  # psycopg["binary"]
from psycopg.rows import dict_row


HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT"))
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HASHLIB_KEY = os.getenv("HASHLIB_KEY")

hashids = Hashids(salt=HASHLIB_KEY, min_length=8)


pool: psycopg.AsyncConnection | None = None


async def connect():
    global pool
    try:
        pool = await psycopg.AsyncConnection.connect(
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            user=USER,
            password=PASSWORD,
            autocommit=True,
            row_factory=dict_row,
            sslmode='require'
        )
        print("Connected to DB")
    except Exception as e:
        print("Failed to connect to DB:", e)


async def set_user(id, username, name):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    encoded = hashids.encode(id)
    async with pool.cursor() as conn:
        await conn.execute(
            "SELECT status FROM users WHERE id = %s;",
            (id,)
        )
        row = await conn.fetchone()
        if not row:
            await conn.execute(
                """
                INSERT INTO users (id, username, name, user_hash)
                VALUES (%s, %s, %s, %s);
                """,
                (id, username, name, encoded)
            )
        else:
            pass


async def check_admin(id):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.cursor() as cur:
        await cur.execute(
            "SELECT status FROM users WHERE id = %s;",
            (id,)
        )
        row = await cur.fetchone()
        return row["status"] if row else None


async def get_all_users():
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.cursor() as cur:
        await cur.execute("SELECT id FROM users;")
        rows = await cur.fetchall()
        return [row["id"] for row in rows]


async def get_my_hash(user_id):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.cursor() as cur:
        await cur.execute("SELECT user_hash FROM users WHERE id = %s::bigint;", (user_id,))
        row = await cur.fetchone()
        return row["user_hash"] if row else None


async def get_name_by_id(id):
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.cursor() as cur:
        await cur.execute("SELECT name FROM users WHERE id = %s;", (id,))
        row = await cur.fetchone()
        return row["name"] if row else None
