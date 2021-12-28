from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import config
import BotTexts


ADMIN_MENU, ADMIN_ALLMES, ADMIN_CHOOSETXT, ADMIN_NEWTXT, ADMIN_CHANGETXT = map(chr, range(10, 15))


def admin_start(update, context):
    context.user_data.clear()
    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton('Ответы пользователей')],
        [KeyboardButton('Редактировать текст сообщений')],
        [KeyboardButton('Выход')]
    ], one_time_keyboard=True, resize_keyboard=True)
    text = 'Админ меню'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_keyboard)
    return ADMIN_MENU


def admin_allmes(update, context):
    conn = sqlite3.connect(config.BD_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM data;')
    all_data = cursor.fetchall()
    conn.close()

    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton('Админ меню')],
        [KeyboardButton('Выход')]
    ], one_time_keyboard=True, resize_keyboard=True)
    text = 'История последних 50 ответов:\n'
    for data in all_data[:-52:-1]:
        text += f'{data}\n'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_keyboard)
    return ADMIN_ALLMES


def admin_choose_text(update, context):
    keyboards = []
    for key in BotTexts.all_message.keys():
        keyboards.append([KeyboardButton(key)])
    keyboards.append([KeyboardButton('Админ меню')])
    keyboards.append([KeyboardButton('Выход')])
    reply_keyboard = ReplyKeyboardMarkup(keyboards, one_time_keyboard=True, resize_keyboard=True)

    text = 'Выберите какое сообщение отредактировать:\n\n'
    for key, mes in BotTexts.all_message.items():
        text += f'{key}: {mes}\n********************\n\n'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_keyboard)
    return ADMIN_CHOOSETXT


def admin_new_text(update, context):
    context.user_data['text_key'] = update.message.text

    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton('Админ меню')],
        [KeyboardButton('Выход')]
    ], one_time_keyboard=True, resize_keyboard=True)
    text = 'Напишите новое сообщение'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_keyboard)
    return ADMIN_NEWTXT


def admin_change_text(update, context):
    new_text = update.message.text
    text_key = context.user_data['text_key']

    BotTexts.all_message[text_key] = new_text

    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton('Админ меню')],
        [KeyboardButton('Выход')]
    ], one_time_keyboard=True, resize_keyboard=True)
    text = 'Новове сообщение сохранено.'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_keyboard)
    context.user_data.clear()
    return ADMIN_CHANGETXT


def admin_cancel(update, context):
    text = 'Выход из админ диалога'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return ConversationHandler.END
