#!/usr/bin/env python3
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CORPUS, FLOOR, PLOSHAD, FLAT, PHOTO, NEWNAME, VIS, CONTACT, CONFIRMATION = range(9)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '3', '6', '19.1']]
    user = update.message.from_user
    user_data = context.user_data
    category = 'Имя'
    text = user.full_name
    user_data[category] = text
    update.message.reply_text(
        'Привет! \n'
        'Этот бот поможет авторизоваться в закрытом чате жильцов своего корпуса ЖК Белая Дача Парк. '
        'В процессе работы бот задаст вам несколько вопросов  и запросит подтверждение того что вы действительно '
        'являетесь собственником квартиры (подойдёт скриншот из личного кабинета с адресом дома и квартиры, '
        'фотография договора с адресом и т.п.). После завершения введённые данные будут направлены администратору '
        'группы корпуса для проверки. \n'
        'Администраторы группы корпуса обязуются не передавать эти данные третьим лица без вашего прямого согласия.\n\n'
        'Для выхода из диалога введите /cancel \n\n'
        'Для продолжения выберите номер корпуса',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )

    return CORPUS


def corpus(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Номер корпуса'
    text = update.message.text
    user_data[category] = text
    logger.info("Corpus of %s: %s", user.name, update.message.text)
    addr = {'1': ' по адресу: мкр. Парковый, д. 1, корп. 3.',
            '3': ' по адресу: мкр. Парковый, д. 1, корп. 1.',
            '6': ' по адресу: мкр. Парковый, д. 1, корп. 4.',
            '19.1': ' ,адрес не присвоен.'}
    update.message.reply_text(
        'Вы выбрали корпус ' + text + addr[text] + '\n\n'
        'Теперь напишите номер вашего этажа.',
    )

    return FLOOR


def floor(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Этаж'
    text = update.message.text
    user_data[category] = text
    logger.info("Floor of %s: %s", user.name, update.message.text)
    update.message.reply_text(
        'Хорошо, теперь напишите площадь квартиры',
    )

    return PLOSHAD


def ploshad(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Площадь'
    text = update.message.text
    user_data[category] = text
    logger.info("Area of %s: %s", user.name, update.message.text)
    update.message.reply_text(
        'Напишите актуальный номер квартиры',
    )

    return FLAT


def flat(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Квартира'
    text = update.message.text
    user_data[category] = text
    logger.info("Flat of %s: %s", user.name, update.message.text)
    update.message.reply_text(
        'Спасибо!\n\n'
        'Теперь вам нужно подтвердить владение квартирой в этом корпусе.\n\n'
        'Пришлите скриншот из личного кабинета ПИК или фото договора, в которых отчётливо виден адрес дома.\n'
        'Прочие личные данные можно замазать.',
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Да', 'Нет'], ['Да, но сменить имя']]
    user = update.message.from_user
    user_data = context.user_data
    photo_file = update.message.photo[-1].get_file()
    userid = user.id
    filename = str(userid) + '_user_photo.jpg'
    photo_file.download(filename)
    category = 'Подтверждение'
    user_data[category] = 'Да'
    logger.info("Photo of %s: %s", user.name, filename)
    update.message.reply_text(
        'Отлично.\n\n'
        'Вы согласны на размещение вашего ника Telegram ('
        + user.full_name +
        ') и номера квартиры в общей таблице жильцов корпуса? '
        'Она будет открыта для участников чата корпуса.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )

    return VIS


def newname(update: Update, context: CallbackContext) -> int:
    return VIS


def vis(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Публикация в таблице жильцов'
    text = update.message.text
    user_data[category] = text
    logger.info("Visable of %s: %s", user.name, update.message.text)

    if user.name[0] == '@':
        reply_keyboard = [['Подтвердить', 'Отказаться']]
        category = 'Имя пользователя'
        text = user.name
        user_data[category] = text
        update.message.reply_text(
            'Хорошо. Пожалуйста, проверьте корректность информации \n\n'
            'Нажмите кнопку Подтвердить для создания заявки на вступление в группу корпуса\n'
            '{}'.format(facts_to_str(user_data)),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)),
        return CONFIRMATION
    else:
        contact_but = KeyboardButton('Отправить номер телефона', request_contact=True)
        reply_keyboard = [[contact_but, 'Веруться']]
        logger.info("Phone of %s: %s", user.name, "Yes")
        update.message.reply_text(
            'В вашем профиле Telegram отсутствует имя пользователя.'
            'Для того чтобы вас можно было добавить в группу, вы можете заполнить параметр Имя пользователя в '
            'настройках профиля и вернуться к началу, '
            'либо указать номер телефона в качестве контактных данных.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)),
        return CONTACT


def contact(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Подтвердить', 'Отказаться']]
    user = update.message.from_user
    user_data = context.user_data
    category = 'Номер телефона'
    pnumber = update.message.contact.phone_number
    text = '+' + str(pnumber)
    user_data[category] = text
    logger.info("Contact of %s: %s", user.name, update.message.text)
    update.message.reply_text(
        'Хорошо. Пожалуйста, проверьте корректность информации \n\n'
        'Нажмите кнопку Подтвердить для создания заявки на вступление в группу корпуса\n'
        '{}'.format(facts_to_str(user_data)),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)),
    return CONFIRMATION


def confirmation(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user = update.message.from_user
    corp_admins = {'1': 341319501, '3': 966732442, '6': 565045535, '19.1': 772564363, '9 3/4': 341319501}
    corpus_no = user_data['Номер корпуса']
    corpus_admin = corp_admins[corpus_no]
    logger.info("Admin of %s: %s", corpus_no, corpus_admin)
    logger.info("User %s chat_id is %s", user.full_name, user.id)
    userid = user.id
    filename = str(userid) + '_user_photo.jpg'
    update.message.reply_text("Готово. Информация отправлена администратору чата для проверки. Ожидайте ответа.",
                              reply_markup=ReplyKeyboardRemove())
    context.bot.send_photo(chat_id=corpus_admin, photo=open(filename, 'rb'),
                           caption='Привет, есть заявка на добавление в чат: \n {}'.format(facts_to_str(user_data)))
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Отменено. Для перезапуска бота введите /start в любой момент', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1507723311:AAEaURI34O1hInN5QlebocjP0WUQHPoiy6c", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CORPUS: [MessageHandler(Filters.regex('^(1|3|6|19.1|9 3/4)$'), corpus)],
            FLOOR: [MessageHandler(Filters.text & ~Filters.command, floor)],
            PLOSHAD: [MessageHandler(Filters.text & ~Filters.command, ploshad)],
            FLAT: [MessageHandler(Filters.text & ~Filters.command, flat)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            NEWNAME: [MessageHandler(Filters.text & ~Filters.command, newname)],
            VIS: [MessageHandler(Filters.regex('^(Да|Да, но сменить имя|Нет)$'), vis)],
            CONTACT: [MessageHandler(Filters.contact, contact),
                      MessageHandler(Filters.regex('^(Веруться)$'), start)],
            CONFIRMATION: [MessageHandler(Filters.regex('^(Подтвердить)$'), confirmation),
                           MessageHandler(Filters.regex('^(Отказаться)$'), start)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
