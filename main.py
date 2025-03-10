import os
import sys
import psycopg2
import logging
from psycopg2 import  Error
from dotenv import load_dotenv
from logging import DEBUG
from example_data import ADD_PERSONS, FIND_PERSONS, DELETE_PERSONS


load_dotenv()
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] >> %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=DEBUG
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

    query_create_phones = '''
        CREATE TABLE IF NOT EXISTS phones (
            id_phone serial PRIMARY KEY,
            id_person int NOT NULL,
            phone_number varchar(14) NOT NULL UNIQUE,  -- +XXXYYYZZZZZZZ
            CONSTRAINT fk_person FOREIGN KEY (id_person) references persons(id_person) ON DELETE cascade 
        );
    '''
    if conn.server_version >= 90500:
        substr = 'IF NOT EXISTS'
    else:
        substr = ''
    query_create_index = f'''
            CREATE UNIQUE INDEX {substr} check_email ON persons (
                LOWER (email)
            );
        '''

    try:
        with conn.cursor() as cur:
            logger.debug('Создание таблицы persons')
            cur.execute(query_create_persons)
            logger.debug('Создание таблицы phones')
            cur.execute(query_create_phones)
            logger.debug('Создание индекса')
            cur.execute(query_create_index)
        logger.debug('Фиксация изменений')
        conn.commit()
    except psycopg2.Error as e:
        logger.error(e.diag.message_primary)

    logger.info('База данных успешно создана.')

def add_client(conn, first_name, last_name, email, phones=None):
    query_add_person = f'''
        INSERT INTO persons (first_name, second_name, email) VALUES 
        ({first_name}, {last_name}, {email});
    '''
    try:
        with conn.cursor() as cur:
            logger.debug(f'Добавление клиента {first_name} {last_name} {email}')
            id_person = cur.execute(query_add_person)
            logger.debug(f'id {id_person}')
    except psycopg2.Error as e:
        logger.error(e.diag.message_primary)

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
            logger.debug(f'Postgresql версия {conn.server_version}')
            create_db(conn)
            for person in ADD_PERSONS:
                add_client(conn, **person)
                break
            sys.exit()
            for person in FIND_PERSONS:
                find_client(conn, **person)
            for person in DELETE_PERSONS:
                delete_client(conn, **person)

    except (Exception, Error) as e:
        logger.error(e)
