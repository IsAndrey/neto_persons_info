import os
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
    conn.autocommit = False
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
    except psycopg2.Error as e_postgres:
        logger.error(f'Код ошибки {e_postgres.pgcode} {e_postgres.diag.message_primary}')
        logger.debug('Отмена изменений')
        conn.rollback()
        return False

    try:
        with conn.cursor() as cur:
            logger.debug('Создание индекса')
            cur.execute(query_create_index)
    except psycopg2.errors.DuplicateTable as e_postgres:
        logger.debug(f'Код ошибки {e_postgres.pgcode} {e_postgres.diag.message_primary}')
    except psycopg2.Error as e_postgres:
        logger.error(f'Код ошибки {e_postgres.pgcode} {e_postgres.diag.message_primary}')
        logger.debug('Отмена изменений')
        conn.rollback()
        return False

    logger.debug('Фиксация изменений')
    conn.commit()
    logger.info('База данных успешно создана.')
    return True

def add_client(conn, first_name, last_name, email, phones=None):
    """Функция, позволяющая добавить нового клиента."""
    conn.autocommit = False
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
            id_person = cur.fetchone()[0]
            logger.debug(f'Получен id {id_person}')
            if phones is not None:
                query_phones_params = [{'id_person': id_person, 'phone': phone} for phone in phones]
                logger.info(f'Добавление телефонов {",".join(phones)}')
                cur.executemany(query_add_phones, query_phones_params)
    except psycopg2.Error as e_postgres:
        logger.error(f'Код ошибки {e_postgres.pgcode} {e_postgres.diag.message_primary}')
        logger.debug('Отмена изменений')
        conn.rollback()
        return None
    except Exception as e:
        logger.error(e)
        logger.debug('Отмена изменений')
        conn.rollback()
        return None
    logger.debug('Фиксация изменений')
    conn.commit()
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
                logger.info(f'Добавление телефонов {",".join(phones)} для клиента {client_id}')
                cur.executemany(query_add_phone, query_params_many)
            else:
                logger.info(f'Добавление телефона {phone} для клиента {client_id}')
                cur.execute(query_add_phone, query_params)
        logger.debug('Фиксация изменений')
        conn.commit()
    except psycopg2.Error as e_postgres:
        logger.error(e_postgres.diag.message_primary)
        return False
    logger.info('Данные успешно добавлены в базу.')
    return True

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
    def p(word, q):
        # значение значения, значений
        if str(q)[-1] == '1':
            return word[0:-1] + 'е'
        elif str(q)[-1] in ('2', '3', '4'):
            return word[0:-1] + 'я'
        else:
            return word

    conn.autocommit = True
    search_conditions = ''
    query_params = {}
    if first_name is not None:
        search_conditions += 'AND p.first_name = %(first_name)s '
        query_params['first_name'] = first_name
        logger.debug(f'Установлен параметр поиска first_name {first_name}')
    if last_name is not None:
        search_conditions += 'AND p.second_name = %(last_name)s '
        query_params['last_name'] = last_name
        logger.debug(f'Установлен параметр поиска last_name {last_name}')
    if email is not None:
        search_conditions += 'AND p.email = %(email)s '
        query_params['email'] = email
        logger.debug(f'Установлен параметр поиска email {email}')
    if search_conditions != '':
        search_conditions = search_conditions[4:-1]  #Убираем ненужный AND
    if phone is not None and search_conditions != '':
        search_conditions = f'WHERE ({search_conditions}) OR ph.phone_number = %(phone)s'
        query_params['phone'] = phone
        logger.debug(f'Установлен параметр поиска phone {phone}')
    elif phone is not None and search_conditions == '':
        search_conditions = f'WHERE ph.phone_number = %(phone)s '
        query_params['phone'] = phone
        logger.debug(f'Установлен параметр поиска phone {phone}')
    elif search_conditions != '':
        search_conditions = f'WHERE {search_conditions}'

    find_person_query = f'''
        SELECT DISTINCT p.id_person FROM persons p 
        LEFT JOIN phones ph
        ON p.id_person = ph.id_person
        {search_conditions};
    '''

    try:
        with conn.cursor() as cur:
            logger.info(f'Поиск клиента {",".join([f"{key}={val}" for key, val in query_params.items()])}')
            cur.execute(find_person_query, query_params)
            logger.debug(f'Найдено {cur.rowcount} {p("значений", cur.rowcount)}')
            if get_many and cur.rowcount > 0:
                result = cur.fetchmany(limit)
                logger.debug(f'Получены id клиентов {",".join([str(id[0]) for id in result])}')
            elif cur.rowcount == 1:
                result = cur.fetchone()
                logger.debug(f'Получен id клиента {result[0]}')
            else:
                result = None
    except psycopg2.Error as e_postgres:
        logger.error(f'Код ошибки {e_postgres.pgcode} {e_postgres.diag.message_primary}')
        result = None
    except Exception as e:
        logger.error(e)
        result = None
    
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
            print(conn.autocommit)
            logger.debug(f'Postgreesql версия {conn.server_version}')
            '''
            create_db(conn)
            for person in ADD_PERSONS:
                add_client(conn, **person)
            '''
            for person in FIND_PERSONS:
                find_client(conn, **person)

    except (Exception, Error) as e:
        logger.error(e)
