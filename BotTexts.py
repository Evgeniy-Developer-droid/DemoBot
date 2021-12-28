from datetime import timezone
import config


all_message = {
    'bot_start': 'Привет [user_fullname]!\n'
                 'Напиши, пожалуйста, сколько тебе лет?',
    'bot_sec_question': 'Круто! В [user_text_message] все только начинается! 😉\n'
                        'А где ты родился?',
    'bot_sec_question_fail': 'Напиши, пожалуйста, свой возраст только числом, без текста и символов.',
    'bot_finish': 'Спасибо за ответы! 😉',
    'bot_on_mes': 'Чтобы начать сначала - нажми /start'
}


def get_text_for_message(update, text_key, **kwargs):
    user = update.effective_user
    replace_kw = {
        '[user_fullname]': user.full_name,
        '[user_nick]': user.username if user.username else "anonymous"
    }

    if update.message:
        message_kw = {
            '[user_text_message]': update.message.text,
            '[utc_date_message]': update.message.date.strftime('%d.%m.%y %H:%M'),
            '[admin_date_message]': update.message.date.replace(tzinfo=timezone.utc).astimezone(
                tz=config.TZ_ADMIN).strftime('%d.%m.%y %H:%M')
        }
        for key, val in message_kw.items():
            replace_kw[key] = val

    if update.callback_query:
        query_kw = {
            '[user_text_button]': update.callback_query.message.text,
            '[utc_date_button]': update.callback_query.message.date.strftime('%d.%m.%y %H:%M'),
            '[admin_date_button]': update.callback_query.message.date.replace(tzinfo=timezone.utc).astimezone(
                tz=config.TZ_ADMIN).strftime('%d.%m.%y %H:%M')
        }
        for key, val in query_kw.items():
            replace_kw[key] = val

    text = all_message[text_key]
    for key, val in replace_kw.items():
        if val:
            text = text.replace(key, str(val))
    return text
