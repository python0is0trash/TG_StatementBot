import sqlite3
from config import default_tg_chat_id, administration_dict


# создание псевдо-таблиц
def create_table_users():
    connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
    cursor = connection.cursor()

    # создание псевдо-таблицы пользователей
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_login VARCHAR(40) NOT NULL,
    user_password VARCHAR(40) NOT NULL,
    user_type VARCHAR(40) NOT NULL DEFAULT 'guest',
    is_login BOOL NOT NULL DEFAULT False,
    tg_chat_id INTEGER DEFAULT ('%d'));
    ''' % (int(default_tg_chat_id)))
    for current_user in range(15):
        if current_user == 0:
            user_type = 'admin'
        elif current_user % 3 == 0:
            user_type = 'officer'
        else:
            user_type = 'guest'
        current_user_login = 'user' + str(current_user)
        current_user_password = str(current_user_login) + 'password' + str(current_user)
        cursor.execute("INSERT INTO users (user_login, user_password, user_type) VALUES ('%s', '%s', '%s');"
                       % (current_user_login, current_user_password, user_type))
    cursor.execute("INSERT INTO users (user_login, user_password, user_type) VALUES ('Q', 'Q', 'guest');")

    # создание псевдо-таблицы обращений
    cursor.execute("DROP TABLE IF EXISTS statements")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statements (
    statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user INTEGER NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    user_age INTEGER NOT NULL,
    user_telephone VARCHAR(20) NOT NULL,
    user_address VARCHAR(100) NOT NULL,
    user_edu VARCHAR(20) NOT NULL,
    user_is_legal BOOL NOT NULL DEFAULT False,
    user_language BOOL NOT NULL DEFAULT False,
    user_ill BOOL NOT NULL DEFAULT False,
    user_administration VARCHAR(64) NOT NULL,
    user_department VARCHAR(64) NOT NULL,
    FOREIGN KEY ("from_user") REFERENCES users("user_id"));
    ''')

    cursor.execute("DROP TABLE IF EXISTS officers")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS officers (
    officer_id INTEGER DEFAULT 1,
    officer_administration VARCHAR(64) NOT NULL,
    officer_department VARCHAR(100),
    FOREIGN KEY ("officer_id") REFERENCES users("user_id"),
    FOREIGN KEY ("officer_administration") REFERENCES statements("user_administration"));
    ''')

    cursor.execute("SELECT user_id FROM users WHERE user_type == 'officer';")
    officers = cursor.fetchall()
    print(len(officers))
    count = 0
    officers_count = 0
    key_count = 0
    for key in administration_dict.keys():
        if key_count == 1:
            break
        else:
            for current_officer in officers:
                if officers_count >= len(officers) / 2:
                    break
                else:
                    for i in range(len(administration_dict[str(key)])):
                        cursor.execute(
                            "INSERT INTO officers (officer_id, officer_administration, officer_department) VALUES ('%d', '%s', '%s');"
                            % (int(current_officer[0]), str(key), administration_dict[str(key)][i])
                                       )
                    cursor.execute(
                        "INSERT INTO statements (from_user, user_name, user_age, user_telephone, user_address, user_edu, user_administration, user_department) "
                        "VALUES ('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%s');"
                        % (int(current_officer[0]) - 1, f'user{count}', count + 18, f'8900800757{count % 10}',
                           f'street, {count * 3 + 100}', 'ВО', str(key), 'SOME DEPT')
                                   )
                    count += 1
                officers_count += 1
            key_count += 1

    officers_count = 0
    key_count = 0
    for key in administration_dict.keys():
        if key_count == 0:
            key_count += 1
            pass
        else:
            for current_officer in officers:
                if officers_count <= len(officers) / 2:
                    officers_count += 1
                    pass
                else:
                    for i in range(len(administration_dict[str(key)])):
                        cursor.execute(
                            "INSERT INTO officers (officer_id, officer_administration, officer_department) VALUES ('%d', '%s', '%s');"
                            % (int(current_officer[0]), str(key), administration_dict[str(key)][i])
                                       )
                    cursor.execute(
                        "INSERT INTO statements (from_user, user_name, user_age, user_telephone, user_address, user_edu, user_administration, user_department) "
                        "VALUES ('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%s');"
                        % (int(current_officer[0]) - 1, f'user{count}', count + 18, f'8900800757{count % 10}',
                           f'street, {count * 3 + 100}', 'ВО', str(key), 'SOME DEPT')
                                   )
                    count += 1
                officers_count += 1
            key_count += 1

    cursor.execute("SELECT * FROM officers ORDER BY officer_administration;")

    connection.commit()
    cursor.close()
    connection.close()

# # подключение к базе данных
# connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
#
# # объект в памяти компьютера с методами для проведения SQL-команд,
# # хранения итогов их выполнения (например, части таблицы)
# # и методов доступа к ним
# cursor = connection.cursor()
#
# # работа с базой данных
# cursor.execute("SELECT * FROM officers ORDER BY officer_administration;")
#
# # при получении данных - запись в переменную в программе
# current_note = cursor.fetchall()
#
# # подтверждение изменений в базе данных
# connection.commit()
#
# # освобождение памяти и закрытие подключения к базе данных
# cursor.close()
# connection.close()
