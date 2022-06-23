"""
De Spam Bot
"""

import datetime
import pickle
import atexit
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram.utils.helpers import DEFAULT_20


def exit_handler():
    print('Safe exit, saving data...')
    with open('chat_data.pickle', 'wb') as f:
        pickle.dump(chat_data, f)
    print('Data saved, good to go')

atexit.register(exit_handler)

# from config import TOKEN
TOKEN = "5536751586:AAE4OIUR2XtT-dqCUUrz3zbpR7HwlS9AzBo"
# make sound

# high-end database units
DEFAULT_TIME_IN_CLOWN_JAIL = 10
# chat_data = dict()
# messages_to_delete = set()
# clowns = dict()
# load chat_data
print('Starting the bot')
# check if chat_data.pickle exists
try:
    with open('chat_data.pickle', 'rb') as f:
        print('Loading data...')
        chat_data = pickle.load(f)
        print('Data loaded')
except FileNotFoundError:
    print('No data found, creating new data')
    chat_data = dict()

bot = Bot(token=TOKEN)
dispatcher: Dispatcher = None

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
f"""
DeSpamBot

Доступные команды:
\t /start - приветствие
\t /despam - почистить чат
\t /set_time X - установить время отслеживания сообщений в секундах, текущее значение: {DEFAULT_TIME_IN_CLOWN_JAIL if update.effective_chat.id not in chat_data else chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL']}
\t /help - справка""")

def set_time(update: Update, context: CallbackContext) -> None:
    """Set time in seconds for clowns in jail."""
    try:
        TIME_IN_CLOWN_JAIL = int(context.args[0])
        chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL'] = TIME_IN_CLOWN_JAIL
        update.message.reply_text(f'Сообщения будут удаляться в течении {TIME_IN_CLOWN_JAIL} секунд')
    except:
        update.message.reply_text('Неверный ввод')

def despam_command(update: Update, context: CallbackContext) -> None:
    """Despams the chat."""
    global chat_data
    try:
        # check if there is data for this chat
        if update.effective_chat.id in chat_data:
            for message_id in chat_data[update.effective_chat.id]['messages_to_delete']:
                try:
                    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                except Exception as e:
                    print(e)
            chat_data[update.effective_chat.id]['messages_to_delete'] = set()
            chat_data[update.effective_chat.id]['clowns'] = dict()
    except Exception as e:
        print(e)
        bot.send_message(update.effective_chat.id, text='Мне нужны права администратора, чтобы удалять сообщения')

def reply(update: Update, context: CallbackContext) -> None:
    """Reply to user message."""
    # check if there is data for this chat
    if update.effective_chat.id not in chat_data:
        chat_data[update.effective_chat.id] = dict()
        chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL'] = DEFAULT_TIME_IN_CLOWN_JAIL
        chat_data[update.effective_chat.id]['messages_to_delete'] = set()
        chat_data[update.effective_chat.id]['clowns'] = dict()
    # check if there is a message
    if update.message:
        # check if message from user via bot
        if update.message.via_bot:
            # @HowYourBot?
            if update.message.via_bot.id == 1341194997:
                # add message to set of messages to delete
                chat_data[update.effective_chat.id]['messages_to_delete'].add(update.message.message_id)
                # put user in clowns dict
                chat_data[update.effective_chat.id]['clowns'][update.message.from_user.id] = datetime.datetime.now()
        # check if reply to message
        elif update.message.reply_to_message:
            # check if reply to message from user via @HowYourBot
            if update.message.reply_to_message.message_id in chat_data[update.effective_chat.id]['messages_to_delete']:
                chat_data[update.effective_chat.id]['messages_to_delete'].add(update.message.message_id)
                # put user in clowns dict
                chat_data[update.effective_chat.id]['clowns'][update.message.from_user.id] = datetime.datetime.now()
        # check if this message was sent by a clown
        elif update.message.from_user.id in chat_data[update.effective_chat.id]['clowns']:
            # check if this message was sent in the last TIME_IN_CLOWN_JAIL seconds
            if datetime.datetime.now() - chat_data[update.effective_chat.id]['clowns'][update.message.from_user.id] < datetime.timedelta(seconds=chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL']):
                # add message to set of messages to delete
                chat_data[update.effective_chat.id]['messages_to_delete'].add(update.message.message_id)
            # else remove user from clowns dict
            else:
                del chat_data[update.effective_chat.id]['clowns'][update.message.from_user.id]

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
    print('Bot started')
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    print('Bot stopped')


if __name__ == '__main__':
    main()
