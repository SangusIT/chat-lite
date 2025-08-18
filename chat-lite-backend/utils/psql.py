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
    create_result = None
    if type(table_check) != asyncpg.exceptions.UndefinedTableError:
        return table_check
    try:
        create_result = await psql_conn.execute('''
            CREATE TABLE users(
                user_id INT GENERATED ALWAYS AS IDENTITY UNIQUE,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) UNIQUE,
                key VARCHAR(255) NOT NULL UNIQUE,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    except asyncpg.exceptions.PostgresError as e:
        create_result = e
    finally:
        return create_result

async def create_table_chats(psql_conn, logger):
    table_check = await check_table(psql_conn, 'chats', logger)
    create_result = None
    if type(table_check) != asyncpg.exceptions.UndefinedTableError:
        return table_check
    try:
        create_result = await psql_conn.execute('''
            CREATE TABLE chats(
                chat_id INT GENERATED ALWAYS AS IDENTITY UNIQUE,
                user_id INT,
                CONSTRAINT fk_user 
                    foreign key(user_id)
                        references users(user_id),
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    except asyncpg.exceptions.PostgresError as e:
        create_result = e
    finally:
        return create_result

async def create_table_texts(psql_conn, logger):
    table_check = await check_table(psql_conn, 'texts', logger)
    create_result = None
    if type(table_check) != asyncpg.exceptions.UndefinedTableError:
        return table_check
    try:
        create_result = await psql_conn.execute('''
            CREATE TABLE texts(
                text_id INT GENERATED ALWAYS AS IDENTITY UNIQUE,
                chat_id INT,
                CONSTRAINT fk_chat 
                    foreign key(chat_id)
                        references chats(chat_id),
                mongo_ref INT,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    except asyncpg.exceptions.PostgresError as e:
        create_result = e
    finally:
        return create_result
    
async def table_schema(psql_conn, logger):
    tables = []
    try:
        query = '''
            SELECT 
                table_name, 
                is_insertable_into
            FROM 
                information_schema.tables
            WHERE 
                table_name IN ('users','chats','texts')
        '''
        result = await psql_conn.fetch(query)
        logger.info(result)
        for res in result:
            logger.info(res)
            tables.append(res)
    except Exception as e:
        logger.warning(e)
    finally:
        return tables

async def exec(psql_conn, logger, statment):
    result = ""
    try:
        result = await psql_conn.fetch(statment)
    except Exception as e:
        result = e.message
    finally:
        return result
    
async def exec_many(psql_conn, logger, statment, args):
    result = False
    try:
        result = await psql_conn.executemany(statment, args)
    except Exception as e:
        result = e.message
    finally:
        return result


async def get_user(conn, search_key, search_val, logger):
    stmt = "SELECT * FROM users WHERE %s = '%s'" % (search_key, search_val)
    result = await exec(conn, logger, stmt)
    return result

async def check_key(conn, key, logger):
    stmt = "SELECT * FROM users WHERE key = '%s' LIMIT 1" % key
    result = await exec(conn, logger, stmt)
    return result

async def check_table(psql_conn, table, logger):
    logger.info("Creating %s table." % table)
    check_result = None
    try:
        check_result = await psql_conn.fetchval("SELECT COUNT(*) FROM %s" % table)
    except asyncpg.exceptions.PostgresError as e:
        check_result = e
    finally:
        logger.info(check_result)
        return check_result
    
async def drop_table(psql_conn, table):
    drop_result = None
    try:
        drop_result = await psql_conn.execute("DROP TABLE IF EXISTS %s" % table)
    except asyncpg.exceptions.PostgresError as e:
        drop_result = e
    finally:
        return drop_result