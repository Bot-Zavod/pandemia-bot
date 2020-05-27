from telegram.ext import Updater, Filters, ConversationHandler, MessageHandler, CommandHandler, Handler
import telegram.ext
from telegram import ReplyKeyboardMarkup #KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
import requests
from dotenv import load_dotenv

from os import environ, getcwd
import logging
import datetime
from dateutil import tz


from etc import text
from variables import *
from hospital_needs import get_hospital_needs


load_dotenv()
print("Modules import")


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


########################################
# https://api.pandemiia.in.ua/api_docs/
########################################


REGIONS = {
    1: "Вінницька область",
    2: "Волинська область",
    3: "Дніпропетровська область",
    4: "Донецька область",
    5: "Житомирська область",
    6: "Закарпатська область",
    7: "Запорізька область",
    8: "@conext_error",
    9: "Київська область",
    10: "Кіровоградська область",
    11: "Луганська область",
    12: "@conext_error",
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
    hospital_needs = get_hospital_needs()
    """
    {
        region_id: {
            region_name: text, 
            hospitals: [
                {
                    hospital_name: text,
                    needs: [
                        {
                            need_name: text,
                            needed: int,
                            received: int
                        }
                    ]
                }
            ]
        }
    }
    """
    for region_id, region in hospital_needs.items():
        if region_id in REGIONS:
            msg = f"<b>{region['region_name']}</b>\n\n"
            for hospital in region["hospitals"]:
                h = f"🏥 {hospital['hospital_name']}\n"
                for need in hospital["needs"]:
                    h += f"• <i>{need['need_name']} 🙏{need['needed']}/{need['received']}👍</i>\n"
                msg += h + "\n"
            context.bot.send_message(chat_id=REGIONS[region_id], 
                                     text=msg, 
                                     parse_mode=telegram.ParseMode.HTML)


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
    time_to_work = datetime.time(hour=23, minute=11, second=1, tzinfo=kiev_tz)
    j.run_daily(callback_daily, time_to_work)
    
    necessary_handlers = [CommandHandler('start', start),
                          CommandHandler('stop', done)]

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
