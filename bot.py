import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import os
from get_information import *
from database import create_tables, get_users
from telegram.ext import CallbackContext, CommandHandler, Updater
import sqlite3

class Bot:
    def __init__(self):
        api = os.environ.get("CVBOT_API")

        self.bot = telegram.Bot(token=api)
        self.updater = Updater(token=api, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('subscribe', self.subscribe))
        self.updater.dispatcher.add_handler(CommandHandler('unsubscribe', self.unsubscribe))

        conn = sqlite3.connect(r'covid19.db', check_same_thread=False)
        self.curr = conn.cursor()
        create_tables(self.curr)

        check_job = self.updater.job_queue
        job_minute = check_job.run_repeating(self.check_if_updated, interval=900, first=0)

        self.updater.start_polling()

    '''
    Methods of the commands (which are /start, /subscribe, and /unsubscribe so far.)
    '''

    def start(self, update, context):
        github_keyboard = [[InlineKeyboardButton("GitHub", url='https://github.com/memreyagci/covid-19-telegram-bot')]]
        reply_markup = InlineKeyboardMarkup(github_keyboard)

        self.bot.send_message(chat_id=update.effective_chat.id, text='''Welcome to the COVID-19 Statististics Bot!\n
You can access to the list of countries to subscribe via /subscribe command, and to unsubscribe via /unsubscribe.''')
        self.bot.send_message(chat_id=update.effective_chat.id, text='''Here is the GitHub repo of this bot. You can help me out by contributing and creating issues.''', reply_markup=reply_markup)

    def subscribe(self, update, context):
        #subscribed_list = get_user_subcriptions(self.curr, str(update.effective_user.id))
        subscribed_list = []
        subscription_keyboard = []
        subscription_list = []
        
        for i in get_country_list():
            if i not in subscribed_list:
                subscription_list.append(i)

        print(subscription_list)

        remaining = len(subscription_list) % 3
        print(remaining)

        for i in range(0, len(subscription_list), 3):
            try:
                subscription_keyboard.append(
                        [InlineKeyboardButton(subscription_list[i], url='d.com'),
                        InlineKeyboardButton(subscription_list[i+1], url='d.com'),
                        InlineKeyboardButton(subscription_list[i+2], url='d.com')]
                    )
            except:
                pass
                
        for i in range(remaining):
            subscription_keyboard.append([InlineKeyboardButton(subscription_list[len(subscription_list) - (i+1)], url='d.com')])

        nonuser_reply_markup = InlineKeyboardMarkup(subscription_keyboard)
        self.bot.send_message(chat_id=update.effective_chat.id, text="List to subscribe", reply_markup=nonuser_reply_markup)

    def unsubscribe(self, update, context):
        subscribed_list = get_user_subcriptions(self.curr, str(update.effective_user.id))
        button_list = []

        for i in subscribed_list:
            if i in subscribed_list:
                button_list.append(InlineKeyboardButton("i", callback_data='button_register'))

        
        unsubscription_keyboard = [
            button_list
                        ]

        nonuser_reply_markup = InlineKeyboardMarkup(unsubscription_keyboard)

    ''' 
    END OF COMMAND METHODS.
    '''

    def check_if_updated(self, context: telegram.ext.CallbackContext):
        db_last_statistics = get_db_statistics(self.curr)
        message_country = check_if_updated(self.curr, db_last_statistics)
        if message_country != None:
            message_list = message_country[0]
            country_list = message_country[1]

            if message_list != []:
                for a in message_list:
                    user_list = get_users(self.curr)

                    for i in user_list:
                        if user_list[1] in country:
                            self.bot.send_message(chat_id=i[0], text=message_list[a])



if __name__ == '__main__':
    bot = Bot()
