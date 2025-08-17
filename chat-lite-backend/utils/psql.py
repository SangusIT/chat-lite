import asyncpg
import asyncio
from dotenv import load_dotenv
import os
import json

load_dotenv()

PSQL_USER: str = os.environ.get("PSQL_USER")
PSQL_PASSWORD: str = os.environ.get("PSQL_PASSWORD")
PSQL_HOST: str = os.environ.get("PSQL_HOST")
PSQL_DB: str = os.environ.get("PSQL_DB")

async def create_db():
    psql_conn = None
    result = ""
    try:
        psql_conn = await asyncpg.connect(user=PSQL_USER, password=PSQL_PASSWORD, database=PSQL_DB, host=PSQL_HOST)
        result = "DB previously created."
    except asyncpg.exceptions.PostgresError as e:
        print("DB does not exist.")
        psql_conn = await asyncpg.connect(
            user=PSQL_USER,
            password=PSQL_PASSWORD,
            host=PSQL_HOST
        )
        await psql_conn.execute(
            f'CREATE DATABASE "{PSQL_DB}" OWNER "{PSQL_USER}"'
        )
        result = "DB created."
    finally:
        if psql_conn:
            await psql_conn.close()
        return result

async def create_table_users(psql_conn, logger):
    table_check = await check_table(psql_conn, 'users', logger)
    logger.info(table_check)
    create_result = None
    if type(table_check) != asyncpg.exceptions.UndefinedTableError:
        return create_result
    try:
        create_result = await psql_conn.execute('''
            CREATE TABLE users(
                id serial primary key,
                username text unique,
                email text unique,
                hashed_password text unique,
                key text unique,
                updated_at timestamp,
                created_at timestamp default current_timestamp
            )
        ''')
    except asyncpg.exceptions.PostgresError as e:
        create_result = e
    finally:
        return create_result

async def create_table_chats(psql_conn, logger):
    table_check = await check_table(psql_conn, 'chats', logger)
    logger.info(table_check)
    create_result = None
    if type(table_check) != asyncpg.exceptions.UndefinedTableError:
        return create_result
    try:
        create_result = await psql_conn.execute('''
            CREATE TABLE chats(
                id serial primary key,
                user int references users(id),
                updated_at timestamp,
                created_at timestamp default current_timestamp
            )
        ''')
    except asyncpg.exceptions.PostgresError as e:
        create_result = e
    finally:
        return create_result

async def create_table_texts(psql_conn, logger):
    table_check = await check_table(psql_conn, 'texts', logger)
    logger.info(table_check)
    create_result = None
    if type(table_check) != asyncpg.exceptions.UndefinedTableError:
        return create_result
    try:
        create_result = await psql_conn.execute('''
            CREATE TABLE texts(
                id serial primary key,
                chat int references chats(id),
                role text,
                content text,
                file text,
                updated_at timestamp,
                created_at timestamp default current_timestamp
            )
        ''')
    except asyncpg.exceptions.PostgresError as e:
        create_result = e
    finally:
        return create_result
    
async def table_schema(psql_conn, logger):
    tables = []
    try:
        query = """
        SELECT table_name, column_name, data_type, character_maximum_length, column_default, is_nullable
        from INFORMATION_SCHEMA.COLUMNS where table_name IN ('users','chats','texts');
        """
        result = await psql_conn.fetch(query)
        logger.info(result)
        for res in result:
            logger.info(res)
            tables.append(res)
    except Exception as e:
        logger.warning(e)
    finally:
        return tables
    
async def exec(psql_conn, logger, statment, args):
    result = False
    try:
        result = await psql_conn.executemany(statment[0], args)
        result = True
    except Exception as e:
        logger.warning(e)
    finally:
        return result


async def get_user(conn, username):
    pass

async def check_key(conn, key):
    pass

async def set_password():
    pass

async def check_table(psql_conn, table, logger):
    check_result = None
    try:
        check_result = await psql_conn.fetchval("SELECT COUNT(*) FROM %s" % table)
    except asyncpg.exceptions.PostgresError as e:
        check_result = e
    finally:
        return check_result
    
async def drop_table(psql_conn, table):
    drop_result = None
    try:
        drop_result = await psql_conn.execute("DROP TABLE IF EXISTS %s" % table)
    except asyncpg.exceptions.PostgresError as e:
        drop_result = e
    finally:
        return drop_result