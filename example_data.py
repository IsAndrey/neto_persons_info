ADD_PERSONS = [
    {'first_name': 'Иван', 'last_name': 'Иванов', 'email': 'i.ivanov@mydomain.ru'},
    {'first_name': 'Петр', 'last_name': 'Петров', 'email': 'p.petrov@mydomain.ru', 'phones': ['+79173300221']},
    {'first_name': 'Петр', 'last_name': 'Иванов', 'email': 'p.ivanov@mydomain.ru', 'phones': ['+79173300222', '+79173300225']},
    {'first_name': 'Иван', 'last_name': 'Петров', 'email': 'i.petrov@mydomain.ru', 'phones': ['+79173300223', '+79173300226']},
    {'first_name': 'Иванко', 'last_name': 'Иванов', 'email': 'I.IVANko@mydomain.ru', 'phones': []}
]

DELETE_PERSONS = [
    {'first_name': 'Иван', 'last_name': 'Иванов', 'email': 'i.ivanov@mydomain.ru', 'phones': []},
    {'first_name': 'Петр', 'last_name': 'Петров', 'email': 'p.petrov@mydomain.ru', 'phones': ['+79173300221']},
    {'first_name': 'Петр', 'last_name': 'Иванов', 'email': 'p.ivanov@mydomain.ru', 'phones': ['+79173300222', '+79173300222']},
    {'first_name': 'Иван', 'last_name': 'Петров', 'email': 'i.petrov@mydomain.ru', 'phones': ['+79173300223', '+79173300221']},
    {'first_name': 'Иванко', 'last_name': 'Иванов', 'email': 'I.IVANOV@mydomain.ru', 'phones': []}
]

FIND_PERSONS = [
    {'first_name': 'Иван',   'last_name': 'Иванов', 'email': 'i.ivanov@mydomain.ru', 'phone': None},
    {'first_name': None,     'last_name':  None,    'email': None,                   'phone': '+79173300221'},
    {'first_name': 'Петр',   'last_name': 'Иванов', 'email': '',                     'phone': '+79173300222'},
    {'first_name': None,     'last_name': None,     'email': 'p.ivanov@mydomain.ru', 'phone': '+79173300223', 'get_many': True},
    {'first_name': 'Иванко', 'last_name': 'Иванов', 'email': None,                   'phone': None},
    {'get_many': True, 'limit': 5}
]