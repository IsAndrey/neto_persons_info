import os
import sys
import psycopg2
import logging
from psycopg2 import Error
from dotenv import load_dotenv
from logging import INFO, DEBUG
from example_data import ADD_PERSONS, FIND_PERSONS, DELETE_PERSONS


load_dotenv()
if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] >> %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=DEBUG
    )
else:
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] >> %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=INFO
    )
logger = logging.getLogger(__name__)

def create_db(conn):
    """Функция, создающая структуру БД (таблицы)."""
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
    except psycopg2.Error as e_postgres:
        logger.error(e_postgres.diag.message_primary)

    logger.info('База данных успешно создана.')

def add_client(conn, first_name, last_name, email, phones=None):
    """Функция, позволяющая добавить нового клиента."""
    query_add_person = '''
        INSERT INTO persons (first_name, second_name, email) VALUES 
        (%(first_name)s, %(last_name)s, %(email)s)
        RETURNING id_person;
    '''
    query_params = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }
    query_add_phones = '''
        INSERT INTO phones (id_person, phone_number)
        VALUES (%(id_person)s, %(phone)s);
    '''
    try:
        with conn.cursor() as cur:
            logger.info(f'Добавление клиента {first_name} {last_name} {email}')
            cur.execute(query_add_person, query_params)
            id_person = cur.fetchone()
            logger.debug(f'Получен id {id_person}')
            if phones is not None:
                query_phones_params = [{'id_person': id_person, 'phone': phone} for phone in phones]
                cur.executemany(query_add_phones, query_phones_params)
        logger.debug('Фиксация изменений')
        conn.commit()
    except psycopg2.Error as e_postgres:
        logger.error(e_postgres.diag.message_primary)
        return None
    except Exception as e:
        logger.error(e)
        return None
    logger.info('Данные успешно добавлены в базу.')
    return id_person

def add_phone(conn, client_id, phone='', many=False, phones=None):
    """Функция, позволяющая добавить телефон для существующего клиента."""
    query_add_phone = '''
        INSERT INTO phones (id_person, phone_number)
        VALUES (%(id_person)s, %(phone)s)
        RETURNING *
    '''
    query_params = {
        'id_person': client_id,
        'phone': phone
    }

    try:
        with conn.cursor() as cur:
            if many:
                query_params_many = [{'id_person': client_id, 'phone': phone} for phone in phones]
                logger.info(f'Добавление телефонов {phones} для клиента {client_id}')
                cur.executemany(query_add_phone, query_params_many)
            else:
                logger.info(f'Добавление телефона {phone} для клиента {client_id}')
                cur.execute(query_add_phone, query_params)
        logger.debug('Фиксация изменений')
        conn.commit()
    except psycopg2.Error as e_postgres:
        logger.error(e_postgres.diag.message_primary)
        return None
    logger.info('Данные успешно добавлены в базу.')

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None,
                  delete_current_phones=False):
    """Функция, позволяющая изменить данные о клиенте."""
    query_fields = ''
    query_values = ''
    change_query_params = {}
    for key, val in {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }.items():
        if val is not None:
            query_fields += f', {key}'
            query_values += f', %({key})s'
            change_query_params[key] = val
            logger.debug(f'Установлено поле для изменения {key} значение {val}')
    '''
    if first_name is not None:
        query_fields += ', first_name'
        query_values += ', %(first_name)s'
        change_query_params['first_name'] = first_name
        logger.debug(f'Установлено поле для изменения first_name значение {first_name}')
    if last_name is not None:
        query_fields += ', last_name'
        query_values += ', %(last_name)s'
        change_query_params['last_name'] = last_name
        logger.debug(f'Установлено поле для изменения last_name значение {last_name}')
    if email is not None:
        query_fields += ', email'
        query_values += ', %(email)s'
        change_query_params['email'] = email
        logger.debug(f'Установлено поле для изменения email значение {email}')
    '''
    if query_fields != '' and query_fields != '':
        query_fields = query_fields[2:]
        query_values = query_values[2:]
        change_query_params['id_person'] = client_id
        change_person_query = f'''
            UPDATE persons SET ({query_fields}) = ({query_values})
            WHERE id_person = %(id_person)s;
        '''
    else:
        change_person_query = None
        change_query_params = None

    if delete_current_phones:
        delete_query_params = {'id_person': client_id}
        delete_phones_query = f'''
            DELETE FROM phones WHERE id_person = %(id_person)i;
        '''
    else:
        delete_query_params = None

    if phones is not None:
        ...

    with conn.cursor() as cur:
        if change_person_query is not None:
            cur.execute(change_person_query, change_query_params)
        if delete_phones_query is not None:
            cur.execute(delete_phones_query, delete_query_params)

def delete_phone(conn, client_id, phone):
    pass

def delete_client(conn, client_id):
    pass

def find_client(conn, first_name=None, last_name=None, email=None, phone=None, get_many=False, limit=10):
    """Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону."""
    search_conditions = ''
    query_params = {}
    if first_name is not None and isinstance(first_name, str):
        search_conditions += 'AND p.first_name = %(first_name)s '
        query_params['first_name'] = first_name
        logger.debug(f'Установлен параметр поиска first_name {first_name}')
    if last_name is not None and isinstance(last_name, str):
        search_conditions += 'AND p.last_name = %(last_name)s '
        query_params['last_name'] = last_name
        logger.debug(f'Установлен параметр поиска last_name {last_name}')
    if email is not None and isinstance(email, str):
        search_conditions += 'AND p.email = %(email)s '
        query_params['email'] = email
        logger.debug(f'Установлен параметр поиска email {email}')
    if phone is not None and isinstance(phone, str):
        search_conditions += 'OR  ph.phone = %(phone)s '
        query_params['phone'] = phone
        logger.debug(f'Установлен параметр поиска phone {phone}')
    if search_conditions != '':
        search_conditions = 'WHERE ' + search_conditions[4:-1]

    find_person_query = f'''
        SELECT DISTINCT id_person FROM persons p 
        LEFT JOIN phones ph
        ON p.id_person = ph.id_person
        {search_conditions};
    '''

    try:
        with conn.cursor() as cur:
            logger.info(f'Поиск клиента')
            cur.execute(find_person_query)
            logger.debug(f'Найдено {cur.rowcount} значений')
            if get_many and cur.rowcount > 0:
                result = cur.fetchmany(limit)
                logger.debug(f'Получены id клиентов {result}')
            elif cur.rowcount == 1:
                result = cur.fetchone()
                logger.debug(f'Получен id клиента {result}')
            else:
                result = None
    except psycopg2.Error as e_postgres:
        logger.error(e_postgres.diag.message_primary)
        return None
    
    if result is not None:
        logger.info('Поиск успешно завершен')
    else:
        logger.info('Поиск не дал результатов')

    return result


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
