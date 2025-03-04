
-- Создание таблиц
CREATE TABLE IF NOT EXISTS persons (
    id_person serial PRIMARY KEY,
    first_name varchar(50) NOT NULL,
    second_name varchar(50) NOT NULL,
    email varchar(50) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS check_email ON persons (
    LOWER (email)
);

CREATE TABLE IF NOT EXISTS phones (
    id_phone serial PRIMARY KEY,
    id_person int NOT NULL,
    phone_number varchar(14) NOT NULL UNIQUE,  -- +XXXYYYZZZZZZZ
    CONSTRAINT fk_person FOREIGN KEY (id_person) references persons(id_person) ON DELETE cascade 
);

TRUNCATE TABLE persons CASCADE;

-- Добавление новых сотрудников
INSERT INTO persons (first_name, second_name, email) VALUES 
('Иван', 'Иванов', 'i.ivanov@mydonain.com'),
('Петр', 'Петров', 'p.petrov@mydonain.com'),
('Дмитрий', 'Дмитриев', 'd.dmitriev@mydonain.com'),
('Кирилл', 'Кириллов', 'k.kirillov@mydonain.com'),
('Иван', 'Иванов', 'ii.ivanov@mydonain.com');

-- Добавление телефона существующего сотрудинка
INSERT INTO phones (id_person, phone_number)
(
    SELECT p.id_person, '+79997777777'
    FROM persons p 
    WHERE p.id_person = 8
)

-- Удалить телефон существующего клиента
DELETE FROM phones WHERE id_person = 8 AND phone_number = '+79997777777'

--Добавление нового сотрудника
WITH new_person AS (
    INSERT INTO persons (first_name, second_name, email) VALUES
    ('Иван', 'Иванов', 'i3.ivanov@mydonain.com')
    RETURNING id_person
)
INSERT INTO phones (id_person, phone_number)
(
    SELECT new_person.id_person, '+76669999999'
    FROM new_person
    UNION
    SELECT new_person.id_person, '+75559999999'
    FROM new_person
);

--Поиск сотрудника
SELECT * FROM persons p 
LEFT JOIN phones ph
ON p.id_person = ph.id_person
WHERE phone_number IN ('+76669999999');

--Изменение данных о клиенте
UPDATE persons SET (second_name, first_name) = ('Иванидзе', 'Ивано')
WHERE id_person = 12;

DELETE FROM phones WHERE id_person = 12;

INSERT INTO phones (id_person, phone_number) VALUES 
(12, '+74449999999'),
(12, '+76669999999')
;


