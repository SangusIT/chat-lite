import asyncpg
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

PSQL_USER: str = os.environ.get("PSQL_USER")
PSQL_PASSWORD: str = os.environ.get("PSQL_PASSWORD")
PSQL_HOST: str = os.environ.get("PSQL_HOST")
PSQL_DB: str = os.environ.get("PSQL_DB")

async def create_db():
    psql_client = None
    try:
        psql_client = await asyncpg.connect(user=PSQL_USER, password=PSQL_PASSWORD, database=PSQL_DB, host=PSQL_HOST)
        print("DB previously created.")
    except asyncpg.exceptions.PostgresError as e:
        print("DB does not exist.")
        psql_client = await asyncpg.connect(
            user=PSQL_USER,
            password=PSQL_PASSWORD,
            host=PSQL_HOST
        )
        await psql_client.execute(
            f'CREATE DATABASE "{PSQL_DB}" OWNER "{PSQL_USER}"'
        )
        print('DB created.')
    finally:
        if psql_client:
            await psql_client.close()

async def create_users_table():
    pass

async def create_chats_table():
    pass

async def create_texts_table():
    pass

async def get_user(client, username):
    pass

async def check_key(client, key):
    pass

async def set_password():
    pass



# asyncio.run(create_db())