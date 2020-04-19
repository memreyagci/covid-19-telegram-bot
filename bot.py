import os
import sqlite3

import pycountry_convert

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater, CallbackQueryHandler
import logging

from get_information import *
from database import create_tables, get_users, get_nonsubscribed_countries_by_continent, get_user_subscriptions, get_all_countries, get_country_list, check_if_updated, save_user_subscription, remove_user_subscription, get_country_by_continent

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

        self.continents = ["Asia", "Africa", "North America", "South America", "Antarctica", "Europe", "Oceania"]

        for i in self.continents:
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i))

        for i in get_country_list(self.conn, self.curr):
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i[0]))
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='{}_unsubscribe'.format(i[0])))
        
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='main'))

        check_job = self.updater.job_queue
        job_minute = check_job.run_repeating(self.check_updates, interval=180, first=0)

        self.updater.start_polling()
        print("started")

    '''
    Methods of the commands (which are /start, /subscribe, and /unsubscribe so far.)
    '''

    def start(self, update, context):
        github_keyboard = [[InlineKeyboardButton("GitHub", url='https://github.com/memreyagci/covid-19-telegram-bot')]]
        reply_markup = InlineKeyboardMarkup(github_keyboard)

        self.bot.send_message(chat_id=update.effective_chat.id, text='''Welcome to the COVID-19 Worldwide Statististics Bot!

You can access to the list of countries to subscribe via /subscribe command, and to unsubscribe via /unsubscribe.\nTo see this message again, use the /start command. Command can also be seen via the / (slash) icon below, left of the attachments.''')
        self.bot.send_message(chat_id=update.effective_chat.id, text='''Here is the GitHub repo of this bot. You can help me out by contributing and creating issues.''', reply_markup=reply_markup)

    def subscribe(self, update, context):
        query = update.callback_query
        all_countries = get_all_countries(self.curr)

        if query == None or query.data == "main":
            continents_keyboard = []

            for i in range(0, 7, 2):
                try:
                    continents_keyboard.append([
                            InlineKeyboardButton(self.continents[i], callback_data=self.continents[i]),
                            InlineKeyboardButton(self.continents[i+1], callback_data=self.continents[i+1])
                            ])
                except IndexError:
                    continents_keyboard.append([
                            InlineKeyboardButton(self.continents[i], callback_data=self.continents[i])
                            ])
            try:
                update.message.reply_text("Please select the continent which the country you want subscribe to is in", reply_markup=InlineKeyboardMarkup(continents_keyboard))
            except AttributeError:
                self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Please select the continent in which the country you want subscribe to is in", reply_markup=InlineKeyboardMarkup(continents_keyboard))

        elif query.data == "Antarctica":
            selected_continent_keyboard = []

            selected_continent_keyboard.append([
                InlineKeyboardButton("<< Back to continents menu", callback_data="main")
                    ])

            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Looks like no man's land.", reply_markup=InlineKeyboardMarkup(selected_continent_keyboard))

        elif query.data in self.continents:
            selected_continent_keyboard = []

            nonsubscribed_countries = get_nonsubscribed_countries_by_continent(self.curr, update.effective_user.id, query.data)

            for i in range(0, len(nonsubscribed_countries), 3):
                    try:
                        selected_continent_keyboard.append([
                        InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i], get_country_flag(nonsubscribed_countries[i])), callback_data=nonsubscribed_countries[i]),
                        InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i+1], get_country_flag(nonsubscribed_countries[i+1])), callback_data=nonsubscribed_countries[i+1]),
                        InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i+2], get_country_flag(nonsubscribed_countries[i+2])), callback_data=nonsubscribed_countries[i+2]),
                                ])
                    except:
                        selected_continent_keyboard.append([
                        InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i], get_country_flag(nonsubscribed_countries[i])), callback_data=nonsubscribed_countries[i])
                            ])

            selected_continent_keyboard.append([
                InlineKeyboardButton("<< Back to continents menu", callback_data="main")
                    ])

            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Here is the list of the countries in {}".format(query.data), reply_markup=InlineKeyboardMarkup(selected_continent_keyboard))

        elif query.data in all_countries:
            self.country_subscription(update.effective_user.id, query.data)
            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="You are successfully subscribed to {}".format(query.data))
        else:
            self.unsubscribe(update,context)

    def unsubscribe(self, update, context):
        query = update.callback_query
        subscribed_list = get_user_subscriptions(self.curr, str(update.effective_user.id))
        unsubscription_keyboard = []

        if query == None:
            #for i in range(0, len(subscribed_list), 3):
                # try:
                #     unsubscription_keyboard.append([
                #         InlineKeyboardButton('{} {}'.format(subscribed_list[i], get_country_flag(subscribed_list[i])), callback_data='{}_unsubscribe'.format(subscribed_list[i])),
                #         InlineKeyboardButton('{} {}'.format(subscribed_list[i+1], get_country_flag(subscribed_list[i+1])), callback_data='{}_unsubscribe'.format(subscribed_list[i+1])),
                #         InlineKeyboardButton('{} {}'.format(subscribed_list[i+2], get_country_flag(subscribed_list[i+2])), callback_data='{}_unsubscribe'.format(subscribed_list[i+2]))
                #             ])
                # except:
            for i in subscribed_list:
                    unsubscription_keyboard.append([
                        InlineKeyboardButton('{} {}'.format(i, get_country_flag(i)), callback_data='{}_unsubscribe'.format(i))
                            ])
            self.bot.send_message(chat_id=update.effective_chat.id, text="Here are the countries you subscribed to.\nClick to unsubscribe.", reply_markup=InlineKeyboardMarkup(unsubscription_keyboard))
        else:
            for i in subscribed_list:
                if query.data == '{}_unsubscribe'.format(i):
                    query.data = query.data.replace("_unsubscribe", "")
                    self.country_unsubscription(update.effective_user.id, query.data)
                    self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="{} is unsubscribed".format(query.data))
                    break

    ''' 
    END OF COMMAND METHODS.
    '''

    def check_updates(self, context: telegram.ext.CallbackContext):
        country_list = get_country_list(self.conn, self.curr)

        for c in country_list:
            if check_if_updated(self.conn, self.curr, c[0]) != False:
                users = get_users(self.curr)
                message_to_send = generate_update_message(c[0])
                for u in users:
                    if c[0] == u[1]:
                        self.bot.send_message(chat_id=u[0], text=message_to_send)

    def country_subscription(self, user_id, query):
        save_user_subscription(self.conn, self.curr, user_id, query)

    def country_unsubscription(self, user_id, query):
        remove_user_subscription(self.conn, self.curr, user_id, query)


if __name__ == '__main__':
    bot = Bot()