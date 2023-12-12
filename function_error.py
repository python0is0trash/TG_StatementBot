from telebot import types
from config import bot, link_back


def program_error(message, text_hint='Ошибка выполнения запроса', do_add_button_back=False):
    chat_id = message.chat.id

    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(text='🔗 Ссылка для обратной связи', url=link_back))

    if do_add_button_back:
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_start'))
    bot.send_message(chat_id=SOME_CHAT,
                     text=f'Произошла ошибка!\n\n'
                          f''
                          f'Код ошибки: {str(text_hint).split("/")[0] + str(text_hint).split("/")[1]}')
    bot.send_message(chat_id=chat_id,
                     text=f'Произошла ошибка!\n\n'
                          f''
                          f'Код ошибки: {str(text_hint).split("/")[0]}\n\n'
                          f''
                          f'Сообщение об ошибке успешно отправлено автору бота!',
                     reply_markup=markup_inline)
