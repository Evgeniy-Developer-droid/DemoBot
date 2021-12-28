from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from BotTexts import get_text_for_message
from datetime import datetime
import os.path
import logging
import sqlite3
import config
import admin


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
print("Бот запущен")

HOW_OLD, WHERE_BORN = map(chr, range(2))


def create_table_bd():
    conn = sqlite3.connect(config.BD_NAME)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE data (
        
        data TEXT,
        user_id INTEGER,
        user_name TEXT,
        user_nick TEXT,
        question TEXT,
        answer TEXT
    
    );""")

    conn.commit()
    conn.close()


def update_chat_info(update):
    chat = update.effective_chat
    user = update.effective_user
    message = update.message if update.message else None
    user_fullname = user.full_name
    user_nick = user.username if user.username else "anonymous"
    query = update.callback_query if update.callback_query else None
    return chat, user, message, query, user_nick, user_fullname


def bot_start(update, context):
    chat, user, message, query, user_nick, user_fullname = update_chat_info(update)
    text = get_text_for_message(update, 'bot_start')
    context.bot.send_message(chat_id=chat.id, text=text)
    return HOW_OLD


def bot_sec_question(update, context):
    chat, user, message, query, user_nick, user_fullname = update_chat_info(update)
    try:
        user_age = int(message.text)
        text = get_text_for_message(update, 'bot_sec_question')
        context.bot.send_message(chat_id=chat.id, text=text)

        conn = sqlite3.connect(config.BD_NAME)
        cursor = conn.cursor()
        bd_value = (datetime.now().strftime('%d.%m.%y %H:%M'), user.id, user_fullname, user_nick, 'Вопрос 1', user_age)
        cursor.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?, ?);', bd_value)
        conn.commit()
        conn.close()
        return WHERE_BORN
    except:
        user_text = message.text
        text = get_text_for_message(update, 'bot_sec_question_fail')
        context.bot.send_message(chat_id=chat.id, text=text)
        return HOW_OLD


def bot_finish(update, context):
    chat, user, message, query, user_nick, user_fullname = update_chat_info(update)
    user_place = message.text
    text = get_text_for_message(update, 'bot_finish')
    context.bot.send_message(chat_id=chat.id, text=text)

    conn = sqlite3.connect(config.BD_NAME)
    cursor = conn.cursor()
    bd_value = (datetime.now().strftime('%d.%m.%y %H:%M'), user.id, user_fullname, user_nick, 'Вопрос 2', user_place)
    cursor.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?, ?);', bd_value)
    conn.commit()
    conn.close()
    return ConversationHandler.END


def bot_on_mes(update, context):
    chat, user, message, query, user_nick, user_fullname = update_chat_info(update)
    text = get_text_for_message(update, 'bot_on_mes')
    context.bot.send_message(chat_id=chat.id, text=text)


def main_bot():
    if not os.path.exists(config.BD_NAME):
        create_table_bd()

    updater = Updater(config.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    flt_prvt_txt = Filters.chat_type.private & Filters.text & (~Filters.command)
    menu_conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", bot_start, Filters.chat_type.private),
            CommandHandler("admin", admin.admin_start, Filters.chat_type.private),
        ],
        states={
            HOW_OLD: [MessageHandler(flt_prvt_txt, bot_sec_question)],
            WHERE_BORN: [MessageHandler(flt_prvt_txt, bot_finish)],

            admin.ADMIN_MENU: [
                MessageHandler(flt_prvt_txt & Filters.text('Ответы пользователей'), admin.admin_allmes),
                MessageHandler(flt_prvt_txt & Filters.text('Редактировать текст сообщений'), admin.admin_choose_text),
            ],
            admin.ADMIN_ALLMES: [],
            admin.ADMIN_CHOOSETXT: [
                MessageHandler(flt_prvt_txt & Filters.text('Выход'), admin.admin_cancel),
                MessageHandler(flt_prvt_txt & Filters.text('Админ меню'), admin.admin_start),
                MessageHandler(flt_prvt_txt, admin.admin_new_text),
            ],
            admin.ADMIN_NEWTXT: [
                MessageHandler(flt_prvt_txt & Filters.text('Выход'), admin.admin_cancel),
                MessageHandler(flt_prvt_txt & Filters.text('Админ меню'), admin.admin_start),
                MessageHandler(flt_prvt_txt, admin.admin_change_text),
            ],
        },
        fallbacks=[
            MessageHandler(flt_prvt_txt & Filters.text('Выход'), admin.admin_cancel),
            MessageHandler(flt_prvt_txt & Filters.text('Админ меню'), admin.admin_start),
        ],
    )

    dispatcher.add_handler(menu_conv)
    dispatcher.add_handler(MessageHandler(flt_prvt_txt, bot_on_mes))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main_bot()
