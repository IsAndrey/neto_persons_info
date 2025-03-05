import os
import psycopg2
import logging
from psycopg2 import  Error
from dotenv import load_dotenv
from logging import INFO


load_dotenv()
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] >> %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=INFO
)
logger = logging.getLogger(__name__)

def create_db(conn):
    """Создаение таблиц базы данных"""
    query_create_persons = '''
        CREATE TABLE IF NOT EXISTS persons (
            id_person serial PRIMARY KEY,
            first_name varchar(50) NOT NULL,
            second_name varchar(50) NOT NULL,
            email varchar(50) NOT NULL
        );
    '''
    query_create_index = '''
        CREATE UNIQUE INDEX IF NOT EXISTS check_email ON persons (
            LOWER (email)
        );
    '''
    query_create_phones = '''
        CREATE TABLE IF NOT EXISTS phones (
            id_phone serial PRIMARY KEY,
            id_person int NOT NULL,
            phone_number varchar(14) NOT NULL UNIQUE,  -- +XXXYYYZZZZZZZ
            CONSTRAINT fk_person FOREIGN KEY (id_person) references persons(id_person) ON DELETE cascade 
        );
    '''
    try:
        logger.debug('Создание таблицы persons')
        conn.execute(query_create_persons)
        logger.debug('Создание индекса')
        conn.execute(query_create_index)
        logger.debug('Создание таблицы phones')
        conn.execute(query_create_phones)
    except psycopg2.Error as e:
        logger.error(e.diag.message_primary)

    logger.info('База данных успешно создана.')

def add_client(conn, first_name, last_name, email, phones=None):
    pass

def add_phone(conn, client_id, phone):
    pass

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    pass

def delete_phone(conn, client_id, phone):
    pass

def delete_client(conn, client_id):
    pass

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    pass


if __name__=='__main__':
    dbname = os.getenv('PG_BASE')
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASS')
    logger.debug('Подключение к базе данных')
    try:
        with psycopg2.connect(dbname=dbname, user=user, password=password) as conn:
            create_db(conn)
    except (Exception, Error) as e:
        logger.error(e)


