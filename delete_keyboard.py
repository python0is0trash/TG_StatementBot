from telebot import types
from config import bot


def delete_reply_markup(message):
    markup = types.ReplyKeyboardRemove()
    msg = bot.send_message(chat_id=message.chat.id, text='Удаление кнопок...', reply_markup=markup)
    bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
