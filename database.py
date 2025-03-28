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


async def add_card(conn, name, price, image_path):
    await conn.execute("INSERT INTO cards (name, price, image_path) VALUES ($1, $2, $3)", name, price, image_path)


async def get_card(conn, card_name):
    return await conn.fetchrow("SELECT name, price, image_path FROM cards WHERE name = $1", card_name)

