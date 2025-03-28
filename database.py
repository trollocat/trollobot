import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

DB_URL = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'


async def init_db():
    return await asyncpg.connect(DB_URL)


async def get_user(conn, user_id, username):
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    if not user:
        await conn.execute("INSERT INTO users (id, username) VALUES ($1, $2)", user_id, username)
        return {"id": user_id, "username": username, "balance": 50, "is_admin": False}
    return dict(user)


async def get_balance(conn, user_id):
    result = await conn.fetchrow("SELECT balance FROM users WHERE id = $1", user_id)
    return result["balance"] if result else 0


async def update_balance(conn, user_id, amount):
    await conn.execute("UPDATE users SET balance = balance + $1 WHERE id = $2", amount, user_id)


async def add_transaction(conn, user_id, trollocat_id, trollocat_price):
    await conn.execute("INSERT INTO transactions (user_id, trollocat_id, transaction_type, amount) VALUES ($1, $2, 'buy', $3)",
                       user_id, trollocat_id, trollocat_price)


async def add_trollocat(conn, name, price, image_path):
    await conn.execute("INSERT INTO trollocats (name, price, image_path) VALUES ($1, $2, $3)", name, price, image_path)


async def get_trollocat(conn, trollocat_name):
    return await conn.fetchrow("SELECT * FROM trollocats WHERE name = $1", trollocat_name)


async def get_trollocats_from_user(conn, user_id):
    return await conn.fetch("SELECT * FROM trollocats WHERE id IN (SELECT trollocat_id FROM transactions WHERE user_id = $1)", user_id)
