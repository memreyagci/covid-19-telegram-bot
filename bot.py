import os
import sqlite3

import pycountry_convert

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater, CallbackQueryHandler
import logging

from get_information import *
from database import create_tables, get_users, get_user_subscriptions, get_country_list, check_if_updated, save_user_subscription

class Bot:
    def __init__(self):
        api = os.environ.get("CVBOT_API")
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

        self.conn = sqlite3.connect(r'covid19.db', check_same_thread=False)
        self.curr = self.conn.cursor()
        create_tables(self.curr)

        self.bot = telegram.Bot(token=api)
        self.updater = Updater(token=api, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('subscribe', self.subscribe))
        self.updater.dispatcher.add_handler(CommandHandler('unsubscribe', self.unsubscribe))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='Asia'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='Africa'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='North America'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='South America'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='Antarctica'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='Europe'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='Oceania'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='main'))

        for i in get_country_list(self.conn, self.curr):
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i[0]))

        check_job = self.updater.job_queue
        #job_minute = check_job.run_repeating(self.check_updates, interval=180, first=0)

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
        query = update.callback_query
        all_countries_continents = get_country_list(self.conn, self.curr)
        user_subscriptions = get_user_subscriptions(self.curr, update.effective_user.id)

        to_subscribe = []
        subscription_keyboard = []

        user_id = update.effective_user.id

        continents = {
                "Asia": [],
                "Africa": [],
                "North America": [],
                "South America": [],
                "Antarctica": [],
                "Europe": [],
                "Oceania": []
                }

        for i in all_countries_continents:
            if i[0] not in user_subscriptions:
                to_subscribe.append(i)

        if query == None or query.data == "main":
            continents_keyboard = []

            for i in range(0, len(continents.keys()), 2):
                try:
                    continents_keyboard.append([
                            InlineKeyboardButton(list(continents.keys())[i], callback_data=list(continents.keys())[i]),
                            InlineKeyboardButton(list(continents.keys())[i+1], callback_data=list(continents.keys())[i+1])
                            ])
                except IndexError:
                    continents_keyboard.append([
                            InlineKeyboardButton(list(continents.keys())[i], callback_data=list(continents.keys())[i])
                            ])

            try:
                update.message.reply_text("Please select the continent which the country you want subscribe to is in", reply_markup=InlineKeyboardMarkup(continents_keyboard))
            except AttributeError:
                self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Please select the continent in which the country you want subscribe to", reply_markup=InlineKeyboardMarkup(continents_keyboard))

        elif query.data in continents.keys():
            selected_continent_keyboard = []

            for i in range(len(to_subscribe)):
                if to_subscribe[i][1] == query.data:
                    try:
                        selected_continent_keyboard.append([
                        InlineKeyboardButton(to_subscribe[i][0], callback_data=to_subscribe[i][0])
                                ])
                    except:
                        selected_continent_keyboard.append([
                        InlineKeyboardButton(to_subscribe[i][0], callback_data=to_subscribe[i][0])
                            ])

            selected_continent_keyboard.append([
                InlineKeyboardButton("<< Back to continents menu", callback_data="main")
            ])

            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="List of the countries in {}".format(query.data), reply_markup=InlineKeyboardMarkup(selected_continent_keyboard))

        else:
            for i in all_countries_continents:
                if query.data == i[0]:
                    self.country_subscription(update.effective_user.id, query.data)
                    self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="You are successfully subsribed to {}".format(query.data))
                    break


    def unsubscribe(self, update, context):
        subscribed_list = get_user_subscriptions(self.curr, str(update.effective_user.id))
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

    def check_updates(self, context: telegram.ext.CallbackContext):
        country_list = get_country_list(self.conn, self.curr)

        for c in country_list:
            print(c[0])
            if check_if_updated(self.conn, self.curr, c[0]) != False:
                users = get_users(self.curr)
                message_to_send = generate_update_message(c[0])
                for u in users:
                    if c[0] == u[1]:
                        self.bot.send_message(chat_id=u[0], text=message_to_send)

    def country_subscription(self, user_id, query):
        save_user_subscription(self.conn, self.curr, user_id, query)

if __name__ == '__main__':
    bot = Bot()