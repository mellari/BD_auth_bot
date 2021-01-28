#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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

CORPUS, FLAT, PHOTO, VISABLE, CONFIRMATION = range(5)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1']]

    update.message.reply_text(
        'Приветствуем! Этот бот поможет авторизоваться в закрытом чате жильцов своего корпуса.\n\n'
        'Для выхода из диалога введите /cancel \n\n'
        'Для продолжения выберите номер корпуса',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )

    return CORPUS


def corpus(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Corpus'
    text = update.message.text
    user_data[category] = text
    logger.info("Corpus of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Хорошо, теперь напишите номер квартиры в корпусе или этаж/площадь',
    )

    return FLAT


def flat(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_data = context.user_data
    category = 'Flat'
    text = update.message.text
    user_data[category] = text
    logger.info("Flat of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Спасибо!\n\n'
        'Теперь вам нужно подтвердить владение квартирой в этом корпусе\n\n'
        'Пришлите скриншот из личного кабинета ПИК или фото ДДУ, в которых отчётливо виден адрес дома',
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Да', 'Нет']]
    user = update.message.from_user
    user_data = context.user_data
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    category = 'Screenshot'
    user_data[category] = 'Yes'
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Отлично.\n\n'
        'Вы согласны на размещение вашего ника Telegram и номера квартиры в общей таблице жильцов корпуса?'
        'Она будет открыта для участников чата корпуса.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )

    return VISABLE


def visable(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Отправить админу', 'Не отправлять']]
    user = update.message.from_user
    user_data = context.user_data
    category = 'Visable'
    text = update.message.text
    user_data[category] = text
    logger.info("Visable of %s: %s", user.first_name, update.message.text)
    update.message.reply_text("Хорошо. Пожалуйста, проверьте корректность информации"
                              "{}".format(facts_to_str(user_data)),
                              ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)),

    return ConversationHandler.END


def confirmation(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user = update.message.from_user
    update.message.reply_text("Готово. Информация отправлена администратору чата для проверки",
                              reply_markup=ReplyKeyboardRemove())
    context.bot.send_photo(chat_id=341319501, photo=open('user_photo.jpg', 'rb'),
                           caption="Новый участник чата корпуса пишет: \n {}".format(
                               facts_to_str(user_data)) +
                                   "For more information, message the poster".format(user.name)),

    return ConversationHandler.END


#    context.bot.send_message(chat_id='341319501', text=user.name)

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
            CORPUS: [MessageHandler(Filters.regex('^(1)$'), corpus)],
            FLAT: [MessageHandler(Filters.text & ~Filters.command, flat)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            VISABLE: [MessageHandler(Filters.regex('^(Да|Нет)$'), visable)],
            CONFIRMATION: [MessageHandler(Filters.regex('^Отправить админу$'), confirmation),
                           MessageHandler(Filters.regex('^Не отправлять$'), start)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
