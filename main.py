"""
De Spam Bot
"""

import datetime
import sys, pickle, atexit, signal, traceback
from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.utils.helpers import DEFAULT_20


def exit_handler():
    print('Safe exit, saving data...')
    with open('chat_data.pickle', 'wb') as f:
        pickle.dump(chat_data, f)
    print('Data saved, good to go')

atexit.register(exit_handler)
signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)

# from config import TOKEN
TOKEN = "5536751586:AAE4OIUR2XtT-dqCUUrz3zbpR7HwlS9AzBo"
# make sound

# high-end database units
DEFAULT_TIME_IN_CLOWN_JAIL = 10     # in seconds
DEFAULT_CLEANUP_TIME = 15           # in minutes
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

# bot functions
def clean_chat(update: Update, context: CallbackContext) -> None:
    """Clean up chat."""
    global chat_data
    try:
        # check if there is data for this chat
        if update.effective_chat.id in chat_data:
            for message_id in chat_data[update.effective_chat.id]['messages_to_delete']:
                try:
                    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                except Exception as e:
                    print(e)
            # reset message and user data for the chat
            chat_data[update.effective_chat.id]['messages_to_delete'] = set()
            chat_data[update.effective_chat.id]['clowns'] = dict()
            # update the last cleanup time
            chat_data[update.effective_chat.id]['LAST_CLEANUP_TIME'] = datetime.datetime.now()
    except Exception as e:
        print(e)
        bot.send_message(update.effective_chat.id, text='Мне нужны права администратора, чтобы удалять сообщения')

def ensure_correct_chat_data(update: Update, context: CallbackContext) -> None:
    """Set default values for chat_data."""
    global chat_data
    # check if there is data for this chat
    if update.effective_chat.id not in chat_data:
        chat_data[update.effective_chat.id] = dict()
        chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL'] = DEFAULT_TIME_IN_CLOWN_JAIL
        chat_data[update.effective_chat.id]['CLEANUP_TIME'] = DEFAULT_CLEANUP_TIME
        chat_data[update.effective_chat.id]['AUTOCLEANUP_ENABLED'] = True
        chat_data[update.effective_chat.id]['LAST_CLEANUP_TIME'] = datetime.datetime.now()
        chat_data[update.effective_chat.id]['messages_to_delete'] = set()
        chat_data[update.effective_chat.id]['clowns'] = dict()

# command handlers
def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    ensure_correct_chat_data(update, context)
    match update.effective_chat.type:
        case 'group' | 'supergroup':
            update.message.reply_text(
"""
Хэй, это DeSpamBot бот
\t— Надоел спам от @HowYourBot?
Я умею чистить всё что с ним связано по одной команде /despam

Не забудь выдать мне права администратора в чате, иначе я не смогу удалять сообщения.
"""
            )    
        case 'private':
            update.message.reply_text(
"""
Хэй, это DeSpamBot бот
\t— Надоел спам от @HowYourBot?
Добавь меня в чат и я смогу чистить всё что с ним связано по одной команде /despam

Не забудь выдать мне права администратора в чате, иначе я не смогу удалять сообщения.
"""
            )
        case _:
            pass

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    ensure_correct_chat_data(update, context)
    update.message.reply_text(
f"""
DeSpamBot

Доступные команды:
\t /start - приветствие
\t /despam - очистить чат
\t /set_deletion_period X - установить время отслеживания сообщений, текущее значение: {chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL']} секунд
\t /auto_cleanup_toggle - переключить автоматическое очищение чата, сейчас {"включено" if chat_data[update.effective_chat.id]['AUTOCLEANUP_ENABLED'] else "выключено"}
\t /set_cleanup_period X - установить время автоматической очистки чата, текущее значение: {chat_data[update.effective_chat.id]['CLEANUP_TIME']} минут
\t /help - справка""")

def set_deletion_period_command(update: Update, context: CallbackContext) -> None:
    """Set time in seconds for clowns in jail."""
    ensure_correct_chat_data(update, context)
    try:
        TIME_IN_CLOWN_JAIL = int(context.args[0])
        chat_data[update.effective_chat.id]['TIME_IN_CLOWN_JAIL'] = TIME_IN_CLOWN_JAIL
        update.message.reply_text(f'Сообщения будут удаляться в течении {TIME_IN_CLOWN_JAIL} секунд')
    except Exception as e:
        print(e)
        update.message.reply_text('Неверный ввод')

def set_cleanup_period_command(update: Update, context: CallbackContext) -> None:
    """Set time in minutes between cleanups."""
    ensure_correct_chat_data(update, context)
    try:
        CLEANUP_TIME = int(context.args[0])
        chat_data[update.effective_chat.id]['CLEANUP_TIME'] = CLEANUP_TIME
        update.message.reply_text(f'Очистка чата будет производиться автоматически каждые {CLEANUP_TIME} минут')
    except Exception as e:
        print(e)
        update.message.reply_text('Неверный ввод')

def auto_cleanup_toggle_command(update: Update, context: CallbackContext) -> None:
    """Toggle automated cleanup command."""
    ensure_correct_chat_data(update, context)
    if update.effective_chat.id in chat_data:
        chat_data[update.effective_chat.id]['AUTOCLEANUP_ENABLED'] = not chat_data[update.effective_chat.id]['AUTOCLEANUP_ENABLED']
        if chat_data[update.effective_chat.id]['AUTOCLEANUP_ENABLED']:
            update.message.reply_text(f'Очистка чата будет производиться автоматически каждые {chat_data[update.effective_chat.id]["CLEANUP_TIME"]} минут')
            # set last cleanup time to now
            chat_data[update.effective_chat.id]['LAST_CLEANUP'] = datetime.datetime.now()
        else:
            update.message.reply_text(f'Автоматическая очистика отключена')

def despam_command(update: Update, context: CallbackContext) -> None:
    """Despams the chat."""
    ensure_correct_chat_data(update, context)
    clean_chat(update, context)

def reply(update: Update, context: CallbackContext) -> None:
    """Reply to user message."""
    ensure_correct_chat_data(update, context)
    # check if there is a message
    if update.message:
        # check if autocleanup is enabled
        if chat_data[update.effective_chat.id]['AUTOCLEANUP_ENABLED']:
            if not chat_data[update.effective_chat.id]['LAST_CLEANUP_TIME']:
                chat_data[update.effective_chat.id]['LAST_CLEANUP_TIME'] = datetime.datetime.now()
            # check if cleanup time has passed
            if chat_data[update.effective_chat.id]['LAST_CLEANUP_TIME'] + datetime.timedelta(minutes=chat_data[update.effective_chat.id]['CLEANUP_TIME']) < datetime.datetime.now():
                # do the cleanup
                clean_chat(update, context)

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
    dispatcher.add_handler(CommandHandler("set_deletion_period", set_deletion_period_command, run_async=True))
    dispatcher.add_handler(CommandHandler("set_cleanup_period", set_cleanup_period_command, run_async=True))
    dispatcher.add_handler(CommandHandler("auto_cleanup_toggle", auto_cleanup_toggle_command, run_async=True))

    dispatcher.add_handler(CommandHandler("despam", despam_command, run_async=True))

    # on non command i.e message
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))

    # Start the Bot
    print('Bot started')
    print('Press Ctrl-C to stop')
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    print('Bot stopped')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
        exit_handler()
    except Exception:
        print("Shutdown requested...exiting")
        traceback.print_exc(file=sys.stdout)
        exit_handler()
    except SystemExit:
        print("Shutdown requested...exiting")
        exit_handler()
    sys.exit(0)
    
