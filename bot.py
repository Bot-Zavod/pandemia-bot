from telegram.ext import Updater, Filters, ConversationHandler, MessageHandler, CommandHandler, Handler
import telegram.ext
from telegram import ReplyKeyboardMarkup #KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from os import environ, getcwd # for environmental variables
import logging  #used for error detection
import requests
import datetime
from dateutil import tz


from etc import text
from variables import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


from dotenv import load_dotenv
load_dotenv()
print("Start was succesfull")

########################################
# https://api.pandemiia.in.ua/api_docs/
########################################


REGION_CHOICES = {
    1: "Вінницька область",
    2: "Волинська область",
    3: "Дніпропетровська область",
    4: "Донецька область",
    5: "Житомирська область",
    6: "Закарпатська область",
    7: "Запорізька область",
    8: "Івано-Франківська область",
    9: "Київська область",
    10: "Кіровоградська область",
    11: "Луганська область",
    12: "Львівська область",
    13: "Миколаївська область",
    14: "Одеська область",
    15: "Полтавська область",
    16: "Рівненська область",
    17: "Сумська область",
    18: "Тернопільська область",
    19: "Харківська область",
    20: "Херсонська область",
    21: "Хмельницька область",
    22: "Черкаська область",
    23: "Чернівецька область",
    24: "Чернігівська область",
    25: "м. Київ",
    26: "АР Крим"
}


def find_info(region):
    url = f"https://api.pandemiia.in.ua/hospitals/needs/{region}/"
    info = requests.get(url).json()
    return info


def town_handler(update, context):
    answer = update.message.text
    # if answer == "Одесса":
    info = find_info(answer)
    # elif answer == "Львов":
    #     info = find_info(answer)
    # else:
    #     return start(update, context)

    update.message.reply_text(text="Вот что мне удалось найти")
    update.message.reply_text(text=info["solution"]["code"])


def start(update, context):
    # choose the town
    update.message.reply_text(text="Привет")
    
    url = "https://api.pandemiia.in.ua/hospitals/list-short/"

    regions = requests.get(url).json()
    keyboard_buttons = [[str(town["id"])] for town in regions["results"]]
    # markup = ReplyKeyboardMarkup(keyboard = , resize_keyboard=True)
    update.message.reply_text(text="Выбери свой регион")# reply_markup=markup)
    return TOWN


def callback_daily(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id="@conext_error", 
                             text='A single message with 30s delay')


def done(update, context):
    context.bot.send_message('Bot is dead.\nPress /start to make him ALIVE!')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    api_key = environ.get('API_KEY')
    u = Updater(token=api_key, use_context=True)
    d = u.dispatcher

    j = u.job_queue
    kiev_tz = tz.gettz("Europe/Kiev")
    time_to_work = datetime.time(hour=16, minute=5, second=0, tzinfo=kiev_tz)
    j.run_daily(callback_daily, time_to_work)
    
    necessary_handlers = [CommandHandler('start', start),
                          CommandHandler('stop', done)]
                        #   CommandHandler('admin', admin)]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            TOWN:                 [MessageHandler(Filters.text, town_handler)],
            # MAIN_MENU:            [*necessary_handlers, MessageHandler(Filters.text, main_menu)],
            # MAIN_MENU_HANDLER:    [*necessary_handlers, MessageHandler(Filters.text, main_menu_handler)],
            # ABOUT_YANGEL:         [*necessary_handlers, MessageHandler(Filters.text, about_yangel)],
            # ABOUT_YANGEL_HANDLER: [*necessary_handlers, MessageHandler(Filters.text, about_yangel_handler)]

        },

        fallbacks=[CommandHandler('stop', done)], allow_reentry=True
    )
    d.add_handler(conv_handler)
    #dispatcher.add_error_handler(error)

    u.start_polling()
    print("start succesfull")
    u.idle()


if __name__ == '__main__':
    main()
