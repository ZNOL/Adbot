import pymysql
import pygsheets
from config import *


def commit_execute(sql, values=None):
    with pymysql.connect(
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,

    ) as con:
        with con.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                con.commit()
                logging.info(f'OK: {sql}')
            except Exception as e:
                logging.error(str(e))


def fetchone_execute(sql, values=None):
    with pymysql.connect(
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
    ) as con:
        with con.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                logging.info(f'OK: {sql}')
                return cursor.fetchone()
            except Exception as e:
                logging.error(str(e))
                return ()


def fetchall_execute(sql, values=None):
    with pymysql.connect(
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
    ) as con:
        with con.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                logging.info(f'OK: {sql}')
                return cursor.fetchall()
            except Exception as e:
                logging.error(str(e))
                return ()


def update(id, filed, value, table):
    sql = f"UPDATE `{table}` SET {filed} = %s WHERE id = %s"
    commit_execute(sql, (value, id))


def get_next_id(tableName):
    sql = f"SELECT MAX(id) FROM {tableName}"
    result = fetchone_execute(sql)['MAX(id)']
    if result is None:
        return 1
    else:
        return result + 1


def on_start(createBase=False, createTable=False, showTable=False):
    if createBase:
        sql = f'CREATE DATABASE {DB_DATABASE}'
        with pymysql.connect(
                unix_socket=DB_SOCKET,
                user=DB_USER,
                password=DB_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(sql)
                con.commit()
    if createTable:
        drop_devices_query = 'DROP TABLE IF EXISTS `users`'
        create_devices_query = '''
                CREATE TABLE `users` (
                    `id` bigint NOT NULL PRIMARY KEY,
                    `nickname` nvarchar(100) DEFAULT "",
                    `is_admin` tinyint NOT NULL,
                    `is_client` tinyint NOT NULL,
                    `button_id` int DEFAULT 0,
                    `forward_id` bigint DEFAULT 0,
                    `answers` nvarchar(500) DEFAULT NULL,
                    `companies` nvarchar(500) DEFAULT "{}"
                );
                '''
        drop_buttons_query = 'DROP TABLE IF EXISTS `buttons`'
        create_buttons_query = """
                CREATE TABLE `buttons` (
                    `id` int NOT NULL PRIMARY KEY,
                    `value` nvarchar(100) NOT NULL,
                    `prev_id` int NOT NULL,
                    `next_count` int NOT NULL
                );
                """
        drop_backup_query = 'DROP TABLE IF EXISTS `backup`'
        create_backup_query = """
                CREATE TABLE `backup` (
                    `id` bigint NOT NULL PRIMARY KEY,
                    `today` nvarchar(3000) DEFAULT "[{}, {}]",
                    `yesterday` nvarchar(3000) DEFAULT "[{}, {}]",
                    `week` nvarchar(3000) DEFAULT "[{}, {}]",
                    `2week` nvarchar(3000) DEFAULT "[{}, {}]",
                    `month` nvarchar(3000) DEFAULT "[{}, {}]"
                );
                """
        with pymysql.connect(
                unix_socket=DB_SOCKET,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(drop_devices_query)
                cursor.execute(drop_buttons_query)
                cursor.execute(drop_backup_query)
                con.commit()
                cursor.execute(create_devices_query)
                cursor.execute(create_buttons_query)
                cursor.execute(create_backup_query)
                con.commit()


    if showTable:
        show_devises_query = 'DESCRIBE users'
        show_buttons_query = 'DESCRIBE buttons'
        with pymysql.connect(
                unix_socket=DB_SOCKET,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(show_devises_query)
                result = cursor.fetchall()
                print(*result, sep='\n')
                print()
                cursor.execute(show_buttons_query)
                result = cursor.fetchall()
                print(*result, sep='\n')
                print()


try:
    connection = pymysql.connect(
        unix_socket=DB_SOCKET,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

    on_start(showTable=False, createTable=False)
    gc = pygsheets.authorize(service_file=GOOGLE_ACC_FILEPATH)

    report = gc.open("Отчет")
    # report.share('advkbot@gmail.com', role='writer')

    logging.info('BASE CONNECTED')
except Exception as e:
    print('!', str(e))
    # on_start(createBase=True, createTable=True, showTable=True)
    # report = gc.create("Отчет")
    logging.error(str(e))
