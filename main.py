"""
De Spam Bot
"""

import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram.utils.helpers import DEFAULT_20

# from config import TOKEN
TOKEN = "5536751586:AAE4OIUR2XtT-dqCUUrz3zbpR7HwlS9AzBo"

bot = Bot(token=TOKEN)
dispatcher: Dispatcher = None

# high-end database units
TIME_IN_CLOWN_JAIL = 10
messages_to_delete = set()
clowns = dict()

# command handlers
def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    match update.effective_chat.type:
        case 'group' | 'supergroup':
            update.message.reply_text(
"""
Хей, это DeSpamBot бот
\t— Надоел спам от @HowYourBot?
Я умею чистить всё что с ним связано по одной команде /despam

Не забудь выдать мне права администратора в чате, иначе я не смогу удалять сообщения.
"""
            )    
        case 'private':
            update.message.reply_text(
"""
Хей, это DeSpamBot бот
\t— Надоел спам от @HowYourBot?
Добавь меня в чат и я смогу чистить всё что с ним связано по одной команде /despam

Не забудь выдать мне права администратора в чате, иначе я не смогу удалять сообщения.
"""
            )
        case _:
            pass

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
"""
DeSpamBot

Доступные команды:
\t /start - приветствие
\t /despam - почистить чат
\t /set_time X - установить время отслеживания сообщений в секундах, по умолчанию 10
\t /help - справка""")

def set_time(update: Update, context: CallbackContext) -> None:
    """Set time in seconds for clowns in jail."""
    try:
        TIME_IN_CLOWN_JAIL = int(context.args[0])
        update.message.reply_text(f'Сообщения будут удаляться в течении {TIME_IN_CLOWN_JAIL} секунд')
    except:
        update.message.reply_text('Неверный ввод')

def despam_command(update: Update, context: CallbackContext) -> None:
    """Despams the chat."""
    global messages_to_delete, clowns
    try:
        for message_id in messages_to_delete:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
        messages_to_delete = set()
        clowns = dict()
    except:
        bot.send_message(update.effective_chat.id, text='Мне нужны права администратора, чтобы удалять сообщения')

def reply(update: Update, context: CallbackContext) -> None:
    """Reply to user message."""
    # check if message from user via bot
    if update.message.via_bot:
        # @HowYourBot?
        if update.message.via_bot.id == 1341194997:
            # add message to set of messages to delete
            messages_to_delete.add(update.message.message_id)
            # put user in clowns dict
            clowns[update.message.from_user.id] = datetime.datetime.now()
    # check if reply to message
    elif update.message.reply_to_message:
        # check if reply to message from user via @HowYourBot
        if update.message.reply_to_message.message_id in messages_to_delete:
            messages_to_delete.add(update.message.message_id)
            # put user in clowns dict
            clowns[update.message.from_user.id] = datetime.datetime.now()
    # check if this message was sent by a clown
    elif update.message.from_user.id in clowns:
        # check if this message was sent in the last TIME_IN_CLOWN_JAIL seconds
        if datetime.datetime.now() - clowns[update.message.from_user.id] < datetime.timedelta(seconds=TIME_IN_CLOWN_JAIL):
            # add message to set of messages to delete
            messages_to_delete.add(update.message.message_id)
        # else remove user from clowns dict
        else:
            del clowns[update.message.from_user.id]

# main loop
def main() -> None:
    """Start the bot."""
    global dispatcher

    # Create the Updater and pass it your bot's token.
    updater = Updater(token=TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start_command, run_async=True))
    dispatcher.add_handler(CommandHandler("help", help_command, run_async=True))
    dispatcher.add_handler(CommandHandler("set_time", set_time, run_async=True))

    dispatcher.add_handler(CommandHandler("despam", despam_command, run_async=True))

    # on non command i.e message
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()