from telebot import types
import sqlite3
import phonenumbers

from config import *
# from create_db import create_table_users
from function_error import program_error
from delete_keyboard import delete_reply_markup


# create_table_users()


# декоратор обработки команд от пользователя
@bot.message_handler(commands=['start', 'logout', 'me', 'add_statement', 'my_statements', 'edit_statement', 'edit_user', 'add_administration'])
def current_command(message):
    delete_reply_markup(message=message)
    if message.text == '/start':
        return start_command(message=message)
    elif message.text == '/logout':
        return logout_command(message=message)
    elif message.text == '/me':
        return me_command(message=message)
    elif message.text == '/my_statements':
        return my_statements_command(message=message)
    elif message.text == '/add_statement':
        return start_register(message=message)
    elif message.text == '/edit_statement':
        return edit_statement_command(message=message)
    elif message.text == '/edit_user':
        return edit_user_command(message=message)
    elif message.text == '/add_administration':
        return add_administration_command(message=message)


# стартовое окно выбора метода входа
def start_command(message, do_edit_message=False):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()
        cursor.execute("SELECT is_login FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        do_exit = cursor.fetchone()
        cursor.close()
        connection.close()
        if do_exit and do_exit[0]:
            return logout_command(message=message)
        else:
            users[chat_id] = User()

            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🚪 Войти', callback_data='sign_up'),
                              types.InlineKeyboardButton(text='▶ Зарегистрироваться', callback_data='log_in'))

            if do_edit_message:
                bot.edit_message_text(chat_id=chat_id, message_id=message.message_id,
                                      text='👋 Здравствуйте, желаете войти в систему или зарегистрироваться?',
                                      reply_markup=markup_inline)
            else:
                bot.send_message(chat_id=chat_id,
                                 text='👋 Здравствуйте, желаете войти в систему или зарагистрироваться?',
                                 reply_markup=markup_inline)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии выбора входа в систему).')


# стартовое окно регистрации (окно ввода логина)
def log_in_in_system(message, do_edit_message=False):
    try:
        chat_id = message.chat.id

        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))

        if do_edit_message:
            bot.edit_message_text(chat_id=chat_id, message_id=message.message_id,
                                  text='▶ Введите логин, который вы будете использовать при авторизации в системе в будущем, '
                                       'например \"<b>user1234</b>\".', parse_mode='html', reply_markup=markup_inline)
        else:
            bot.send_message(chat_id=chat_id,
                             text='▶ Введите логин, который вы будете использовать при авторизации в системе в будущем, '
                                  'например \"<b>user1234</b>\".', parse_mode='html', reply_markup=markup_inline)
        bot.register_next_step_handler(message, register_user_password)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии ввода логина (при регистрации)).',
                             do_add_button_back=False)


# окно ввода пароля
def register_user_password(message):
    try:
        chat_id = message.chat.id
        if message.text in commands_list:
            return current_command(message=message)
        elif ' ' in message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введите, пожалуйста, логин без пробелов.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, register_user_password)
        elif '\'--' in message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введите, пожалуйста, корректный логин.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, register_user_password)
        elif message.text:
            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute("SELECT user_login FROM users WHERE user_login == ('%s');" % (str(message.text)))
            login_overlap = cursor.fetchone()
            connection.commit()
            cursor.close()
            connection.close()
            if login_overlap:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))

                bot.send_message(chat_id=chat_id,
                                 text='🚨 Пользователь с таким логином уже существует. Выберите другой логин.',
                                 reply_markup=markup_inline)
                bot.register_next_step_handler(message, register_user_password)
            else:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text='🔁 Ввести другой логин', callback_data='log_in'))

                bot.send_message(chat_id=chat_id,
                                 text='▶ Теперь введите пароль, который вы будете использовать при авторизации в системе в будущем.',
                                 reply_markup=markup_inline)
                bot.register_next_step_handler(message, add_user_to_users, register_login=(message.text).strip())
        else:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))

            bot.send_message(chat_id=chat_id,
                             text='🚨 Введен неверный формат логина. Введите корректный логин.',
                             reply_markup=markup_inline)
            bot.register_next_step_handler(message, register_user_password)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии ввода пароля (при регистрации)).',
                             do_add_button_back=False)


# довавление пользователя в базу данных
def add_user_to_users(message, register_login=None):
    chat_id = message.chat.id
    try:
        if message.text in commands_list:
            return current_command(message=message)
        elif message.text:
            new_user_password = message.text.strip()

            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()

            cursor.execute("INSERT INTO users (user_login, user_password) VALUES ('%s', '%s');"
                           % (str(register_login), str(new_user_password)))

            connection.commit()
            cursor.close()
            connection.close()
            bot.send_message(chat_id=chat_id, text=f'🎉 Пользователь <b>{register_login}</b> успешно зарегистрирован! '
                                                   f'Ваш пароль: <b>{new_user_password}</b>.\n\n'
                                                   f''
                                                   f'🆔 Для продолжения работы необходимо войти в систему.',
                             parse_mode='html')
            return sign_up_in_system(message=message, do_edit_message=False)

        else:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))

            bot.send_message(chat_id=chat_id,
                             text='🚨 Введен неверный формат пароля. Введите корректный пароль.',
                             reply_markup=markup_inline)
            bot.register_next_step_handler(message, add_user_to_users, register_login=register_login)

    except Exception as e:
        return program_error(message=message,
                             text_hint=str(
                                 e) + ' /(ошибка на стадии занесения информации о новом пользователе в базу данных (при авторизации)).',
                             do_add_button_back=False)


# стартовое окно авторизации (окно ввода логина)
def sign_up_in_system(message, do_edit_message=False):
    try:
        chat_id = message.chat.id
        users[chat_id] = User()

        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))

        if do_edit_message:
            bot.edit_message_text(chat_id=chat_id, message_id=message.message_id,
                                  text='👋 Здравствуйте, для начала работы необходимо пройти авторизацию.\n'
                                       'Введите свой логин, указанный при регистрации, например \"<b>user1234</b>\":',
                                  parse_mode='html', reply_markup=markup_inline)
        else:
            bot.send_message(chat_id=chat_id,
                             text='👋 Здравствуйте, для начала работы необходимо пройти регистрацию.\n'
                                  'Введите свой логин, указанный при регистрации, например \"<b>user1234</b>\":',
                             parse_mode='html', reply_markup=markup_inline)
        bot.register_next_step_handler(message, enter_user_login)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии начала авторизации).',
                             do_add_button_back=False)


# окно ввода пароля
def enter_user_login(message):
    chat_id = message.chat.id
    try:
        if not message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введен неверный формат логина. Пожалуйста, введите корректный логин.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, enter_user_login)
        elif message.text in commands_list:
            return current_command(message=message)
        elif ' ' in message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введите, пожалуйста, логин без пробелов.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, enter_user_login)
        elif '\'--' in message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Я знаю, что вы хотите провести SQL-инъекцию... У Вас этого не получится сделать!',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, enter_user_login)
        else:
            current_login = message.text

            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()

            cursor.execute("SELECT user_login FROM users WHERE user_login == ('%s');" % str(current_login))
            logins = cursor.fetchone()

            if logins:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text='🔁 Ввести другой логин', callback_data='sign_up'))
                bot.send_message(chat_id=chat_id,
                                 text=f'✔ Рады видеть вас снова, <b>{current_login}</b>! Теперь введите свой пароль.',
                                 parse_mode='html', reply_markup=markup_inline)
                bot.register_next_step_handler(message, enter_user_password, user_login=current_login)
            else:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
                markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
                bot.send_message(chat_id=chat_id,
                                 text='❌ Пользователя с таким логином не найдено! '
                                      'Введите, пожалуйста, корректный логин или обратитесь в поддержку.',
                                 parse_mode='html', reply_markup=markup_inline)
                bot.register_next_step_handler(message, enter_user_login)

            connection.commit()
            cursor.close()
            connection.close()

    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии ввода логина (при авторизации)).',
                             do_add_button_back=False)


# проверка существования пользователя с данным логином и паролем
def enter_user_password(message, user_login=None):
    chat_id = message.chat.id
    try:
        if not message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(
                types.InlineKeyboardButton(text='🔙 Ввести другой логин', callback_data='input_other_login'))

            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введен неверный формат пароля. Пожалуйста, введите корректный пароль.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, enter_user_password, user_login=user_login)
        elif message.text in commands_list:
            return current_command(message=message)
        elif ' ' in message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(
                types.InlineKeyboardButton(text='🔙 Ввести другой логин', callback_data='input_other_login'))
            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введите, пожалуйста, пароль без пробелов.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, enter_user_password, user_login=user_login)
        elif '\'--' in message.text:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
            markup_inline.add(
                types.InlineKeyboardButton(text='🔙 Ввести другой логин', callback_data='input_other_login'))

            bot.send_message(chat_id=chat_id,
                             text=f'⛔ Введите, пожалуйста, корректный пароль.',
                             parse_mode='html', reply_markup=markup_inline)

            bot.register_next_step_handler(message, enter_user_password, user_login=user_login)
        else:
            current_password = message.text

            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute(
                "SELECT user_id, user_login, user_type, tg_chat_id FROM users WHERE user_login == ('%s') AND user_password == ('%s');"
                % (str(user_login), str(current_password)))
            user_password = cursor.fetchone()

            if user_password:
                users[chat_id].user_login = user_password[1]
                if user_password[3] == default_tg_chat_id:
                    cursor.execute("UPDATE users SET is_login = True, tg_chat_id = ('%d') WHERE user_id == ('%d');" % (
                        int(chat_id), int(user_password[0])))
                else:
                    cursor.execute(
                        "INSERT INTO users (user_login, user_password, user_type, is_login, tg_chat_id) VALUES ('%s', '%s', '%s', True, '%d');"
                        % (str(user_password[1]), str(current_password), str(user_password[2]), int(chat_id)))
                connection.commit()
                cursor.close()
                connection.close()
                return add_statement_command(message=message, is_start_bot=True)
            else:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text='🔗 Поддержка', url=link_back))
                markup_inline.add(
                    types.InlineKeyboardButton(text='🔙 Ввести другой логин', callback_data='input_other_login'))

                bot.send_message(chat_id=chat_id,
                                 text=f'❌ Пользователя <b>{user_login}</b> с таким паролем не найдено! '
                                      'Введите, пожалуйста, корректный пароль или обратитесь в поддержку.',
                                 parse_mode='html', reply_markup=markup_inline)

                bot.register_next_step_handler(message, enter_user_password, user_login=user_login)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии ввода пароля (при авторизации)).',
                             do_add_button_back=False)


def logout_command(message):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT is_login, user_login FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        if not is_user_login_from_db:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                             reply_markup=markup_inline)
        elif is_user_login_from_db[0] == False:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🚪 Да, войти в систему', callback_data='sign_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не вошли в систему! Войти?',
                             reply_markup=markup_inline)
        else:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🔴 Да, выйти из профиля', callback_data='log_out'),
                              types.InlineKeyboardButton(text='🟢 Нет, остаться', callback_data='stay_on_system'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы действительно хотите выйти из профиля <b>{is_user_login_from_db[1]}</b>?',
                             parse_mode='html', reply_markup=markup_inline)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка на стадии выхода из профиля).',
                             do_add_button_back=False)


def me_command(message):
    try:
        chat_id = message.chat.id
        info = (f'<b>Ваше имя в Telegram:</b> {message.from_user.first_name}\n'
                f'<b>Ваш TelegramID:</b> {message.from_user.id}\n')

        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()
        cursor.execute("SELECT user_login, user_password FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()
        cursor.close()
        connection.close()

        if is_user_login_from_db:
            info += (f'<b>Ваш логин в системе:</b> {is_user_login_from_db[0]}\n'
                     f'<b>Ваш пароль от профиля {is_user_login_from_db[0]}:</b> {is_user_login_from_db[1]}')

        bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при загрузке информации о пользователе).',
                             do_add_button_back=False)


def add_statement_command(message, do_edit_message=False, is_start_bot=False):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT is_login, user_login FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()

        cursor.close()
        connection.close()

        if not is_user_login_from_db:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                             reply_markup=markup_inline)
        else:
            if is_start_bot:
                if do_edit_message:
                    bot.edit_message_text(chat_id=chat_id, message_id=message.message_id,
                                          text=f'👮‍♂️ \tБлагодарны Вам за то, что проявили желание проходить службу в ОВД РФ! 👮‍♀️\n'
                                               f'✍ \tЧтобы подать заявление, отправьте боту команду \"/add_statement\".',
                                          parse_mode='html')
                else:
                    bot.send_message(chat_id=chat_id,
                                     text=f'👮‍♂️ \tБлагодарны Вам за то, что проявили желание проходить службу в ОВД РФ! 👮‍♀️\n'
                                          f'✍ \tЧтобы подать заявление, отправьте боту команду \"/add_statement\".',
                                     parse_mode='html')
            # return my_statements_command(message=message)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при загрузке главного меню).',
                             do_add_button_back=False)


def my_statements_command(message, do_edit_message=False):
    try:
        chat_id = message.chat.id

        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT is_login, user_login FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()

        cursor.close()
        connection.close()

        if not is_user_login_from_db:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                             reply_markup=markup_inline)
        else:
            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute("SELECT user_id FROM users WHERE tg_chat_id == ('%d')" % (int(chat_id)))
            current_user = cursor.fetchone()

            cursor.execute("SELECT user_name, user_age, user_telephone, user_address, user_edu, "
                           "user_is_legal, user_language, user_ill, user_administration, user_department "
                           "FROM statements "
                           "WHERE from_user == ('%d');" % (int(current_user[0])))
            all_statements_from_user = cursor.fetchall()

            cursor.close()
            connection.close()
            if all_statements_from_user:
                info = 'Ваши заявления:\n\n'
                for statement in all_statements_from_user:
                    info += (f'<b>Имя</b>: <u>{statement[0]}</u>, <b>Возраст</b>: <u>{statement[1]}</u>, <b>Телефон</b>: <u>{statement[2]}</u>, '
                             f'<b>Адрес проживания</b>: <u>{statement[3]}</u>, <b>Образование</b>: <u>{statement[4]}</u>, '
                             f'<b>Юридическое</b>: <u>{bool_to_text[statement[5]]}</u>, <b>Русский</b>: <u>{bool_to_text[statement[6]]}</u>, '
                             f'<b>Заболевания</b>: <u>{bool_to_text[statement[7]]}</u>, <b>Управление</b>: <u>{statement[8]}</u>, '
                             f'<b>Отдел</b>: <u>{statement[9]}</u>\n-\n')
                info = (info.rstrip())[:-2] + '\n\n'
            else:
                info = 'У Вас нет поданных заявлений. Для подачи нового заявления отправьте команду \"/add_statement\".'

            if do_edit_message:
                bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=info, parse_mode='html')
            else:
                bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии начала заполнения заявления).',
                             do_add_button_back=True)


def start_register(message):
    try:
        chat_id = message.chat.id

        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT is_login, user_login FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()

        cursor.close()
        connection.close()

        if not is_user_login_from_db:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                             reply_markup=markup_inline)
        else:
            bot.send_message(chat_id=chat_id, text='Укажите Ваше ФИО (последнее - при наличии).')
            bot.register_next_step_handler(message, user_name)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии начала заполнения заявления).',
                             do_add_button_back=True)


def user_name(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат имени.\n'
                                                   'Укажите, пожалуйста, верный формат имени...')
            bot.register_next_step_handler(message, user_name)
        elif message.text in commands_list:
            return current_command(message=message)
        else:
            users[chat_id] = User()
            users[chat_id].user_name = message.text
            bot.send_message(chat_id=chat_id, text='Укажите Ваш возраст.')
            bot.register_next_step_handler(message, user_age)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода ФИО (при заполнении заявления)).',
                             do_add_button_back=True)


def user_age(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат возраста.\n'
                                                   'Укажите, пожалуйста, верный формат возраста...')
            bot.register_next_step_handler(message, user_age)
        elif message.text in commands_list:
            return current_command(message=message)
        elif (message.text.isdigit()) and (str(message.text)[0] != '0') and len(message.text) <= 2:
            users[chat_id].user_age = int(message.text)
            bot.send_message(chat_id=chat_id, text='Укажите Ваш номер телефона (в формате \"8ХХХХХХХХХХ\" или \"+7ХХХХХХХХХХ\").')
            bot.register_next_step_handler(message, user_telephone)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат возраста.\n'
                                                   'Укажите, пожалуйста, верный формат возраста...')
            bot.register_next_step_handler(message, user_age)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Возраста (при заполнении заявления)).',
                             do_add_button_back=True)


def user_telephone(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат номера телефона.\n'
                                                   'Укажите, пожалуйста, верный номер телефона...')
            bot.register_next_step_handler(message, user_telephone)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text.isdigit() and phonenumbers.is_valid_number(phonenumbers.parse(number=message.text, region="RU")):
            users[chat_id].user_telephone = str(message.text)
            bot.send_message(chat_id=chat_id, text='Укажите Ваш адрес проживания (в формате \"Область, город, улица, дом\").')
            bot.register_next_step_handler(message, user_address)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат номера телефона.\n'
                                                   'Укажите, пожалуйста, верный номер телефона...')
            bot.register_next_step_handler(message, user_telephone)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Телефона (при заполнении заявления)).',
                             do_add_button_back=True)


def user_address(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат адреса проживания.\n'
                                                   'Укажите, пожалуйста, верный формат адреса проживания...')
            bot.register_next_step_handler(message, user_address)
        elif message.text in commands_list:
            return current_command(message=message)
        elif (len(message.text.split(',')) == 4 and
              not (message.text.split(',')[0].strip().isdigit()) and
              not (message.text.split(',')[1].strip().isdigit()) and
              not (message.text.split(',')[2].strip().isdigit()) and
              (message.text.split(',')[3].strip().isdigit())):

            users[chat_id].user_address = message.text

            current_button = []
            help_list = []
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True,
                                               input_field_placeholder='Укажите образование...',
                                               is_persistent=True,
                                               row_width=5)
            for buttons in range(len(types_of_education)):
                current_button.append(types.KeyboardButton(text=str(types_of_education[buttons])))
                help_list.append(str(types_of_education[buttons]))
            markup.add(*current_button)
            bot.send_message(chat_id=chat_id, text='Укажите Ваше образование.', reply_markup=markup)
            bot.register_next_step_handler(message, user_edu, help_list=help_list)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат адреса проживания.\n'
                                                   'Укажите, пожалуйста, верный формат адреса проживания...')
            bot.register_next_step_handler(message, user_address)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Адреса проживания (при заполнении заявления)).',
                             do_add_button_back=True)


def user_edu(message, help_list=None):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат информации об образовании.\n'
                                                   'Укажите, пожалуйста, Ваше образование...')
            bot.register_next_step_handler(message, user_edu, help_list=help_list)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text in help_list:
            users[chat_id].user_edu = message.text
            if message.text == 'ВО':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                   one_time_keyboard=True,
                                                   input_field_placeholder='У Вас юридическое образование?',
                                                   is_persistent=True,
                                                   row_width=2)
                markup.add(types.KeyboardButton(text='Да'), types.KeyboardButton(text='Нет'))

                bot.send_message(chat_id=chat_id, text='Является ли Ваше образование юридическим?', reply_markup=markup)
                bot.register_next_step_handler(message, user_is_legal)
            else:
                users[chat_id].user_is_legal = False

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                   one_time_keyboard=True,
                                                   input_field_placeholder='Владеете ли Вы русским языком?',
                                                   is_persistent=True,
                                                   row_width=2)
                markup.add(types.KeyboardButton(text='Да'), types.KeyboardButton(text='Нет'))

                bot.send_message(chat_id=chat_id, text='Владеете ли Вы русским языком?', reply_markup=markup)
                bot.register_next_step_handler(message, user_language)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат информации об образовании.\n'
                                                   'Укажите, пожалуйста, Ваше образование...')
            bot.register_next_step_handler(message, user_edu, help_list=help_list)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Образования (при заполнении заявления)).',
                             do_add_button_back=True)


def user_is_legal(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат ответа.\n'
                                                   'Укажите, пожалуйста, является ли Ваше образование юридическим...')
            bot.register_next_step_handler(message, user_is_legal)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text.lower() == 'да' or message.text.lower() == 'нет':
            if message.text.lower() == 'да':
                users[chat_id].user_is_legal = True
            elif message.text.lower() == 'нет':
                users[chat_id].user_is_legal = False

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True,
                                               input_field_placeholder='Владеете ли Вы русским языком?',
                                               is_persistent=True,
                                               row_width=2)
            markup.add(types.KeyboardButton(text='Да'), types.KeyboardButton(text='Нет'))

            bot.send_message(chat_id=chat_id, text='Владеете ли Вы русским языком?', reply_markup=markup)
            bot.register_next_step_handler(message, user_language)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат ответа.\n'
                                                   'Укажите, пожалуйста, является ли Ваше образование юридическим...')
            bot.register_next_step_handler(message, user_is_legal)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии Уточнения типа образования (при заполнении заявления)).',
                             do_add_button_back=True)


def user_language(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат ответа.\n'
                                                   'Укажите, пожалуйста, владеете ли Вы русским языком...')
            bot.register_next_step_handler(message, user_language)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text.lower() == 'да' or message.text.lower() == 'нет':
            if message.text.lower() == 'да':
                users[chat_id].user_language = True
            elif message.text.lower() == 'нет':
                users[chat_id].user_language = False

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True,
                                               input_field_placeholder='Есть ли у Вас хронические заболевания?',
                                               is_persistent=True,
                                               row_width=2)
            markup.add(types.KeyboardButton(text='Да'), types.KeyboardButton(text='Нет'))

            bot.send_message(chat_id=chat_id, text='Есть ли у Вас хронические заболевания?', reply_markup=markup)
            bot.register_next_step_handler(message, user_ill)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат ответа.\n'
                                                   'Укажите, пожалуйста, владеете ли Вы русским языком...')
            bot.register_next_step_handler(message, user_language)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Языка (при заполнении заявления)).',
                             do_add_button_back=True)


def user_ill(message):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат ответа.\n'
                                                   'Укажите, пожалуйста, есть ли у Вас хронические заболевания...')
            bot.register_next_step_handler(message, user_ill)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text.lower() == 'да' or message.text.lower() == 'нет':
            if message.text.lower() == 'да':
                users[chat_id].user_ill = True
            elif message.text.lower() == 'нет':
                users[chat_id].user_ill = False

            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute("SELECT officer_administration FROM officers GROUP BY officer_administration;")
            administrations = cursor.fetchall()
            cursor.close()
            connection.close()

            buttons_administration = []
            help_list = []
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True,
                                               input_field_placeholder='Выберите управление...',
                                               is_persistent=True,
                                               row_width=3)
            for current_administration in administrations:
                buttons_administration.append(types.KeyboardButton(text=str(current_administration[0])))
                help_list.append(str(current_administration[0]).lower())
            markup.add(*buttons_administration)

            bot.send_message(chat_id=chat_id, text='В какое управление Вы хотите подать заявление?', reply_markup=markup)
            bot.register_next_step_handler(message, user_administration, help_list=help_list)
        else:
            bot.send_message(chat_id=chat_id, text='Введен неверный формат ответа.\n'
                                                   'Укажите, пожалуйста, есть ли у Вас хронические заболевания...')
            bot.register_next_step_handler(message, user_ill)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Заболеваний (при заполнении заявления)).',
                             do_add_button_back=True)


def user_administration(message, help_list=None):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Нет такого управления.\n'
                                                   'Укажите, пожалуйста, одно из предложенных управлений, куда Вы хотите подать заявление...')
            bot.register_next_step_handler(message, user_administration)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text.lower() in help_list:
            users[chat_id].user_administration = message.text

            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute("SELECT officer_department FROM officers GROUP BY officer_department;")
            departments = cursor.fetchall()
            cursor.close()
            connection.close()

            buttons_department = []
            help_list = []
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True,
                                               input_field_placeholder='Выберите отдел...',
                                               is_persistent=True,
                                               row_width=3)
            for current_department in departments:
                buttons_department.append(types.KeyboardButton(text=str(current_department[0])))
                help_list.append(str(current_department[0]).lower())
            markup.add(*buttons_department)

            bot.send_message(chat_id=chat_id, text='В какой отдел Вы хотите подать заявление?', reply_markup=markup)
            bot.register_next_step_handler(message, user_department, help_list=help_list)
        else:
            bot.send_message(chat_id=chat_id, text='Нет такого управления.\n'
                                                   'Укажите, пожалуйста, одно из предложенных управлений, куда Вы хотите подать заявление...')
            bot.register_next_step_handler(message, user_administration)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Управления (при заполнении заявления)).',
                             do_add_button_back=True)


def user_department(message, help_list=None):
    try:
        chat_id = message.chat.id
        if not message.text:
            bot.send_message(chat_id=chat_id, text='Нет такого отдела в данном управлении.\n'
                                                   'Укажите, пожалуйста, один из предложенных отделов, куда Вы хотите подать заявление...')
            bot.register_next_step_handler(message, user_department)
        elif message.text in commands_list:
            return current_command(message=message)
        elif message.text.lower() in help_list:
            users[chat_id].user_department = message.text
            return check_user_statement(message=message)
        else:
            bot.send_message(chat_id=chat_id, text='Нет такого отдела в данном управлении.\n'
                                                   'Укажите, пожалуйста, один из предложенных отделов, куда Вы хотите подать заявление...')
            bot.register_next_step_handler(message, user_department)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Отдела (при заполнении заявления)).',
                             do_add_button_back=True)


def check_user_statement(message):
    try:
        chat_id = message.chat.id
        delete_reply_markup(message=message)

        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='✔ Подать заявление', callback_data='send_statement'),
                          types.InlineKeyboardButton(text='❌ Отменить отправку', callback_data='leave_statement'))
        bot.send_message(chat_id=chat_id,
                         text=f'Информация, которую вы желаете предоставить:\n\n'
                              f''
                              f'<b>ФИО</b>: {users[chat_id].user_name}\n'
                              f'<b>Возраст</b>: {users[chat_id].user_age}\n'
                              f'<b>Номер телефона</b>: {users[chat_id].user_telephone}\n'
                              f'<b>Адрес проживания</b>: {users[chat_id].user_address}\n'
                              f'<b>Образование</b>: {users[chat_id].user_edu}\n'
                              f'<b>Есть ли высшее юридическое</b>: {bool_to_text[users[chat_id].user_is_legal]}\n'
                              f'<b>Владеете ли русским языком</b>: {bool_to_text[users[chat_id].user_language]}\n'
                              f'<b>Есть ли хронические заболевания</b>: {bool_to_text[users[chat_id].user_ill]}\n'
                              f'<b>Управление</b>: {users[chat_id].user_administration}\n'
                              f'<b>Отдел</b>: {users[chat_id].user_department}\n\n'
                              f''
                              f'Желаете отправить информацию в отдел?',
                         parse_mode='html',
                         reply_markup=markup_inline)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии ввода Просмотра отправляемой информации (при заполнении заявления)).',
                             do_add_button_back=True)


def statement_to_db(message):
    try:
        chat_id = message.chat.id

        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM users WHERE tg_chat_id == ('%d')" % (int(chat_id)))
        user_tg_id = cursor.fetchone()
        cursor.execute("INSERT INTO statements (from_user, user_name, user_age, user_telephone, user_address, user_edu, "
                       "user_is_legal, user_language, user_ill, user_administration, user_department) "
                       "VALUES ('%d', '%s', '%d', '%s', '%s', '%s', '%d', '%d', '%d', '%s', '%s')"
                       % (
                           int(user_tg_id[0]),
                           str(users[chat_id].user_name),
                           int(users[chat_id].user_age),
                           str(users[chat_id].user_telephone),
                           str(users[chat_id].user_address),
                           str(users[chat_id].user_edu),
                           int(users[chat_id].user_is_legal),
                           int(users[chat_id].user_language),
                           int(users[chat_id].user_ill),
                           str(users[chat_id].user_administration),
                           str(users[chat_id].user_department)
                          )
                       )

        connection.commit()
        cursor.close()
        connection.close()

        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='🏠 На главную', callback_data='stay_on_system'))
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message.message_id,
                              text='✔ Данные успешно отправлены!',
                              reply_markup=markup_inline)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка на стадии занесения введенной пользователем информации в БД (при заполнении заявления)).',
                             do_add_button_back=True)


def statement_out_of_db(message):
    chat_id = message.chat.id
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(text='🏠 На главную', callback_data='stay_on_system'))
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message.message_id,
                          text='❌ Отмена отправки заявления.',
                          reply_markup=markup_inline)


def edit_statement_command(message):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT is_login, user_login FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        if not is_user_login_from_db:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                             reply_markup=markup_inline)
        else:
            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute("SELECT user_id, user_type FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
            officer_id = cursor.fetchone()
            cursor.close()
            connection.close()

            if officer_id[1] == 'guest':
                bot.send_message(chat_id=chat_id, text='⛔ У вас нет прав на редактирование заявлений!')
                return my_statements_command(message=message)
            elif officer_id[1] == 'officer':
                return edit_statement_from_officer(message=message, current_officer_id=officer_id[0], is_admin=False)
            elif officer_id[1] == 'admin':
                return edit_statement_from_officer(message=message, current_officer_id=officer_id[0], is_admin=True)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при обработке команды \"edit_statement\").')


def edit_statement_from_officer(message, current_officer_id=None, is_admin=False):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()
        if is_admin:
            cursor.execute("SELECT statement_id, user_name, user_age, user_telephone, user_address, user_edu, "
                           "user_is_legal, user_language, user_ill, user_administration, user_department FROM statements;")
            all_statements = cursor.fetchall()
            cursor.close()
            connection.close()
            if all_statements:
                info = 'В ИС поступили следующие заявления:\n\n'
                for statement in all_statements:
                    info += (f'<b>ID заявления</b>: <u>{statement[0]}</u>, '
                             f'<b>Имя</b>: <u>{statement[1]}</u>, <b>Возраст</b>: <u>{statement[2]}</u>, <b>Телефон</b>: <u>{statement[3]}</u>, '
                             f'<b>Адрес проживания</b>: <u>{statement[4]}</u>, <b>Образование</b>: <u>{statement[5]}</u>, '
                             f'<b>Юридическое</b>: <u>{bool_to_text[statement[6]]}</u>, <b>Русский</b>: <u>{bool_to_text[statement[7]]}</u>, '
                             f'<b>Заболевания</b>: <u>{bool_to_text[statement[8]]}</u>, <b>Управление</b>: <u>{statement[9]}</u>, '
                             f'<b>Отдел</b>: <u>{statement[10]}</u>\n-\n')
                info = (info.rstrip())[:-2] + '\n\n'
                info += 'Информацию о каком заявителе Вы хотите изменить? Введите сначала его \"ID\", а затем, через разделитель \"|\", другие поля.'
                bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
                bot.register_next_step_handler(message, take_info_from_officer, current_officer_id=current_officer_id,
                                               is_admin=is_admin)
            else:
                info = 'В ИС еще не поступало заявлений.'
                bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
                return add_statement_command(message=message, is_start_bot=True)
        else:
            cursor.execute("SELECT officer_administration FROM officers WHERE officer_id == ('%d')" % (int(current_officer_id)))
            officer_administration = cursor.fetchone()
            cursor.execute("SELECT statement_id, user_name, user_age, user_telephone, user_address, user_edu, "
                           "user_is_legal, user_language, user_ill, user_administration, user_department FROM statements "
                           "WHERE user_administration == ('%s')"
                           % (
                               str(officer_administration[0]))
                           )
            current_officer_statements = cursor.fetchall()
            cursor.close()
            connection.close()
            if current_officer_statements:
                info = 'В Ваше управление поступили следующие заявления:\n\n'
                for statement in current_officer_statements:
                    info += (f'<b>ID заявления</b>: <u>{statement[0]}</u>, '
                             f'<b>Имя</b>: <u>{statement[1]}</u>, <b>Возраст</b>: <u>{statement[2]}</u>, <b>Телефон</b>: <u>{statement[3]}</u>, '
                             f'<b>Адрес проживания</b>: <u>{statement[4]}</u>, <b>Образование</b>: <u>{statement[5]}</u>, '
                             f'<b>Юридическое</b>: <u>{bool_to_text[statement[6]]}</u>, <b>Русский</b>: <u>{bool_to_text[statement[7]]}</u>, '
                             f'<b>Заболевания</b>: <u>{bool_to_text[statement[8]]}</u>, <b>Управление</b>: <u>{statement[9]}</u>, '
                             f'<b>Отдел</b>: <u>{statement[10]}</u>\n-\n')
                info = (info.rstrip())[:-2] + '\n\n'
                info += 'Информацию о каком заявителе Вы хотите изменить? Введите сначала его \"ID\", а затем, через разделитель \"|\", другие поля.'
                bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
                bot.register_next_step_handler(message, take_info_from_officer, current_officer_id=current_officer_id,
                                               is_admin=is_admin)
            else:
                info = 'В Ваше управление еще не поступало заявлений.'
                bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
                return add_statement_command(message=message, is_start_bot=True)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка при просмотре списка всех заявлений).')


def take_info_from_officer(message, current_officer_id=None, is_admin=False):
    try:
        if message.text in commands_list:
            return current_command(message=message)
        else:
            chat_id = message.chat.id
            statement_to_edit = message.text
            statement_to_edit = statement_to_edit.split('|')
            if len(statement_to_edit) == 11:
                connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
                cursor = connection.cursor()
                if is_admin:
                    cursor.execute(
                        "UPDATE statements SET user_name = ('%s'), user_age = ('%d'), user_telephone = ('%s'), user_address = ('%s'), "
                        "user_edu = ('%s'), user_is_legal = ('%d'), user_language = ('%d'), user_ill = ('%d'), "
                        "user_administration = ('%s'), user_department = ('%s') "
                        "WHERE statement_id == ('%d')"
                        % (str(statement_to_edit[1].strip()), int(statement_to_edit[2].strip()),
                           str(statement_to_edit[3].strip()),
                           str(statement_to_edit[4].strip()), str(statement_to_edit[5].strip()),
                           int(statement_to_edit[6].strip()),
                           int(statement_to_edit[7].strip()), int(statement_to_edit[8].strip()),
                           str(statement_to_edit[9].strip()),
                           str(statement_to_edit[10].strip()), int(statement_to_edit[0].strip())
                           )
                    )
                    connection.commit()
                    cursor.close()
                    connection.close()
                    bot.send_message(chat_id=chat_id, text='Заявление успешно отредактировано!')
                    return edit_statement_command(message=message)
                else:
                    cursor.execute(
                        "SELECT officer_administration FROM officers WHERE officer_id == ('%d')" % (int(current_officer_id)))
                    is_right_officer_from_officers = cursor.fetchone()
                    cursor.execute(
                        "SELECT user_administration FROM statements WHERE statement_id == ('%d')" % (int(statement_to_edit[0].strip())))
                    is_right_officer_from_statements = cursor.fetchone()

                    if is_right_officer_from_officers[0] == is_right_officer_from_statements[0]:
                        cursor.execute(
                            "UPDATE statements SET user_name = ('%s'), user_age = ('%d'), user_telephone = ('%s'), user_address = ('%s'), "
                            "user_edu = ('%s'), user_is_legal = ('%d'), user_language = ('%d'), user_ill = ('%d'), "
                            "user_administration = ('%s'), user_department = ('%s') "
                            "WHERE statement_id == ('%d')"
                            % (str(statement_to_edit[1].strip()), int(statement_to_edit[2].strip()), str(statement_to_edit[3].strip()),
                               str(statement_to_edit[4].strip()), str(statement_to_edit[5].strip()), int(statement_to_edit[6].strip()),
                               int(statement_to_edit[7].strip()), int(statement_to_edit[8].strip()), str(statement_to_edit[9].strip()),
                               str(statement_to_edit[10].strip()), int(statement_to_edit[0].strip())
                               )
                        )
                        connection.commit()
                        cursor.close()
                        connection.close()
                        bot.send_message(chat_id=chat_id, text='Заявление успешно отредактировано!')
                        return edit_statement_command(message=message)
                    else:
                        cursor.close()
                        connection.close()
                        bot.send_message(chat_id=chat_id, text='Вы не можете редактировать чужие заявления!')
                        return edit_statement_from_officer(message=message, current_officer_id=current_officer_id, is_admin=is_admin)
            else:
                bot.send_message(chat_id=chat_id, text='Заполнены не все поля!')
                return edit_statement_from_officer(message=message, current_officer_id=current_officer_id, is_admin=is_admin)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при обновлении информации о заявлении).')


def edit_user_command(message):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()

        cursor.execute("SELECT user_id, user_type FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
        is_user_login_from_db = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        if not is_user_login_from_db:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                              types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
            bot.send_message(chat_id=chat_id,
                             text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                             reply_markup=markup_inline)
        else:
            if is_user_login_from_db[1] == 'guest' or is_user_login_from_db[1] == 'officer':
                bot.send_message(chat_id=chat_id, text='⛔ У вас нет прав на редактирование пользователей!')
                return my_statements_command(message=message)
            elif is_user_login_from_db[1] == 'admin':
                return edit_user(message=message, admin_id=is_user_login_from_db[0])
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при обработке команды \"edit_user\").')


def edit_user(message, admin_id=None):
    try:
        chat_id = message.chat.id
        info = 'Сводная информация о пользователях системы:\n\n'
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, user_login, user_password, user_type, is_login, tg_chat_id FROM users")
        all_users = cursor.fetchall()
        for current_user in all_users:
            info += (f'<b>UserID</b>: <u>{current_user[0]}</u>, <b>UserLogin</b>: <u>{current_user[1]}</u>, <b>UserPassword</b>: <u>{current_user[2]}</u>, '
                     f'<b>UserType</b>: <u>{current_user[3]}</u>, <b>UserIsLogin</b>: <u>{bool_to_text[current_user[4]]}</u>, <b>UserTG</b>: <u>{current_user[5]}</u>\n-\n')
        info = (info.rstrip())[:-2] + '\n\n'
        info += (
            'Информацию о каком пользователе вы хотите изменить? Введите сначала его \"UserID\", а затем, через разделитель \"|\", другие поля:\n\n'
            ''
            'login - любая строка\n'
            'password - любая строка\n'
            'type - 1 (admin), 2 (officer), 3 (guest)\n'
            'is login - 0 (не авторизован в системе), 1 (авторизован в системе)\n'
            'tg - любое число')
        bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
        bot.register_next_step_handler(message, edit_current_user, admin_id=admin_id)
    except Exception as e:
        return program_error(message=message,
                             text_hint=str(e) + ' /(ошибка при выводе информации о пользователях системы).')


def edit_current_user(message, admin_id=None):
    try:
        if message.text in commands_list:
            return current_command(message=message)
        else:
            chat_id = message.chat.id
            user_to_edit = message.text
            user_to_edit = user_to_edit.split('|')
            if len(user_to_edit) == 6:
                if (str(user_to_edit[0].strip()).isdigit() and (' ' not in str(user_to_edit[1].strip()))
                        and (' ' not in str(user_to_edit[2].strip())) and (
                                str(user_to_edit[3].strip()) in ['1', '2', '3'])
                        and (int(user_to_edit[4].strip()) in [0, 1]) and (user_to_edit[4].strip()).isdigit()):
                    connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM users WHERE user_login = ('%s')" % (str(user_to_edit[1].strip())))
                    count = cursor.fetchone()
                    if count[0] > 0:
                        bot.send_message(chat_id=chat_id,
                                         text='Пользователь с таким UserLogin уже существует! Пожалуйста, введите другое значение UserLogin.')
                        bot.register_next_step_handler(message, edit_current_user, admin_id=admin_id)
                    else:
                        cursor.execute(
                            "UPDATE users "
                            "SET user_login = ('%s'), user_password = ('%s'), user_type = ('%s'), is_login = ('%d'), tg_chat_id = ('%d') "
                            "WHERE user_id == ('%d')"
                            % (str(user_to_edit[1].strip()), str(user_to_edit[2].strip()),
                               types_of_users[int(user_to_edit[3].strip()) - 1],
                               int(user_to_edit[4].strip()), int(user_to_edit[5].strip()),
                               int(user_to_edit[0].strip())))
                        connection.commit()
                        cursor.close()
                        connection.close()
                        bot.send_message(chat_id=chat_id, text='Пользователь успешно отредактирован!')
                        return edit_user(message=message, admin_id=admin_id)
                else:
                    bot.send_message(chat_id=chat_id,
                                     text='Неверный формат ввода! Пожалуйста, введите данные в корректном формате.')
                    bot.register_next_step_handler(message, edit_current_user, admin_id=admin_id)
            else:
                bot.send_message(chat_id=chat_id, text='Заполнены не все поля!')
                return edit_user(message=message, admin_id=admin_id)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при изменении данных о пользователе).')


def add_administration_command(message):
    chat_id = message.chat.id
    connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
    cursor = connection.cursor()

    cursor.execute("SELECT user_id, user_type FROM users WHERE tg_chat_id == ('%d');" % (int(chat_id)))
    is_user_login_from_db = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    if not is_user_login_from_db:
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='▶ Да, зарегистрироваться', callback_data='log_in'),
                          types.InlineKeyboardButton(text='❌ Нет, остаться', callback_data='back_to_start'))
        bot.send_message(chat_id=chat_id,
                         text=f'Вы не зарегистрированы в системе! Зарегистрироваться?',
                         reply_markup=markup_inline)
    else:
        if is_user_login_from_db[1] == 'guest' or is_user_login_from_db[1] == 'officer':
            bot.send_message(chat_id=chat_id, text='⛔ У вас нет прав на редактирование управлений!')
            return add_statement_command(message=message, is_start_bot=True)
        elif is_user_login_from_db[1] == 'admin':
            return add_administration(message=message)


def add_administration(message):
    chat_id = message.chat.id

    connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
    cursor = connection.cursor()
    cursor.execute("SELECT user_login FROM users WHERE user_type == ('%s')" % 'officer')
    officers_logins = cursor.fetchall()
    cursor.close()
    connection.close()
    count = 1
    info = 'В базе есть сотрудники со следующими логинами:\n\n'
    for current_login in officers_logins:
        info += f'{str(count)}. <u>{current_login[0]}</u>\n'
        count += 1
    info += '\nВведите информацию, которую необходимо добавить, в формате <b>\"Логин | Управление | Отдел\"</b>.'
    bot.send_message(chat_id=chat_id, text=info, parse_mode='html')
    bot.register_next_step_handler(message, add_current_department)


def add_current_department(message):
    chat_id = message.chat.id

    if message.text in commands_list:
        return current_command(message=message)
    else:
        dept_to_edit = message.text
        dept_to_edit = dept_to_edit.split('|')
        if len(dept_to_edit) == 3:
            connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
            cursor = connection.cursor()
            cursor.execute("SELECT user_id, user_type FROM users WHERE user_login == ('%s')" % (str(dept_to_edit[0].strip())))
            is_officer = cursor.fetchone()

            if is_officer[1] == 'officer':
                cursor.execute("INSERT INTO officers (officer_id, officer_administration, officer_department) "
                               "VALUES ('%d', '%s', '%s');"
                               % (int(is_officer[0]), str(dept_to_edit[1].strip()), str(dept_to_edit[2].strip())))
                connection.commit()
                cursor.close()
                connection.close()
                bot.send_message(chat_id=chat_id, text='Данные успешно изменены!')
                return add_statement_command(message=message, is_start_bot=True)
            else:
                bot.send_message(chat_id=chat_id, text='Пользователь с данным логином не является сотрудником!')
                cursor.close()
                connection.close()
                return add_administration_command(message=message)
        else:
            bot.send_message(chat_id=chat_id, text='Заполнены не все поля!')
            return add_administration_command(message=message)


def logout_button(message):
    try:
        chat_id = message.chat.id
        connection = sqlite3.connect('./data_bases/statements_to_work.sqlite3')
        cursor = connection.cursor()
        cursor.execute("SELECT user_login FROM users WHERE tg_chat_id == ('%d')" % (int(chat_id)))
        user_login_help = cursor.fetchone()
        cursor.execute("SELECT COUNT(user_login) FROM users WHERE user_login == ('%s')" % (str(user_login_help[0])))
        count = cursor.fetchone()

        if (count[0]) > 1:
            cursor.execute("DELETE FROM users WHERE tg_chat_id == ('%d')" % (int(chat_id)))
        else:
            cursor.execute(
                "UPDATE users SET is_login = False, tg_chat_id = {} WHERE tg_chat_id == {};".format(
                    int(default_tg_chat_id),
                    int(chat_id)))
        connection.commit()
        cursor.close()
        connection.close()

        return start_command(message=message, do_edit_message=True)
    except Exception as e:
        return program_error(message=message, text_hint=str(e) + ' /(ошибка при выходе из системы).')


@bot.message_handler(content_types=['text'])
def text_from_user(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Неизвестное значение.')


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    try:
        chat_id = callback.message.chat.id
        bot.clear_step_handler_by_chat_id(
            chat_id=chat_id)  # если пользователь нажал на кнопку, то все степ хэндлеры прекращаются

        if callback.data == 'sign_up':
            sign_up_in_system(callback.message, do_edit_message=True)
        elif callback.data == 'log_in':
            log_in_in_system(callback.message, do_edit_message=True)
        elif callback.data == 'input_other_login':
            sign_up_in_system(callback.message, do_edit_message=True)
        elif callback.data == 'back_to_start':
            start_command(callback.message, do_edit_message=True)

        elif callback.data == 'stay_on_system':
            my_statements_command(callback.message, do_edit_message=True)
        elif callback.data == 'log_out':
            logout_button(message=callback.message)

        elif callback.data == 'send_statement':
            statement_to_db(callback.message)
        elif callback.data == 'leave_statement':
            statement_out_of_db(callback.message)
    except Exception as e:
        return program_error(message=callback.message, text_hint=str(e) + ' /(ошибка при нажатии на InlineButton).')


if __name__ == '__main__':
    bot.infinity_polling()
