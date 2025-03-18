import psycopg2

query_add_person = '''
    INSERT INTO persons (first_name, second_name, email) VALUES 
    (%(first_name)s, %(last_name)s, %(email)s)
    RETURNING id_person;
'''
params_add_person = {
    'first_name': 'Каршиев',
    'last_name': 'Абдувалий',
    'email': 'a.karshien@mydomain.com'
}

query_add_person0 = '''
    INSERT INTO persons (first_name, second_name, email) VALUES 
    ('Каршиев', 'Абдувалий', 'a.karshien@mydomain.com')
    RETURNING id_person;
'''

try:
    with psycopg2.connect(dbname='postgres', user='postgres', password='batbat') as connect:
        print(f'Коннект успешен версия postgres {connect.server_version}')
        with connect.cursor() as cursor:
            print(f'Выполнение запроса {query_add_person} с параметрами {params_add_person}')
            cursor.execute(query_add_person, params_add_person)
            print('Успешно!')

except (psycopg2.Error, Exception) as e:
    print(e)