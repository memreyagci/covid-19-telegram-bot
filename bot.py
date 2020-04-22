import os
import sqlite3

import pycountry_convert

import telegram
from telegram.ext import CallbackContext, CommandHandler, Updater, CallbackQueryHandler
import logging

from get_information import *
from database import create_tables, check_new_country, get_users, get_nonsubscribed_countries_by_continent, get_user_subscriptions, get_all_countries, check_if_updated, save_user_subscription, remove_user_subscription, get_country_by_continent
import keyboards_texts

class Bot:
    def __init__(self):
        api = os.environ.get("CVBOT_API")
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

        self.conn = sqlite3.connect(r'covid19.db', isolation_level=None, check_same_thread=False)
        self.curr = self.conn.cursor()
        self.curr_job = self.conn.cursor()
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

        for i in check_new_country(self.conn, self.curr):
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i[0]))
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='{}_unsubscribe'.format(i[0])))
        
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='main'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='main_unsubscribe'))

        check_job = self.updater.job_queue
        job_minute = check_job.run_repeating(self.check_updates, interval=180, first=0)

        self.updater.start_polling()
        print("started")

    '''
    Methods of the commands (which are /start, /subscribe, and /unsubscribe so far.)
    '''

    def start(self, update, context):
        self.bot.send_message(chat_id=update.effective_chat.id, text=keyboards_texts.welcome())
        self.bot.send_message(chat_id=update.effective_chat.id, text=keyboards_texts.github([0]), reply_markup=keyboards_texts.github[1])

    def subscribe(self, update, context):
        query = update.callback_query
        telegram_id = update.effective_user.id
        all_countries = get_all_countries(self.curr)
        
        if query == None or query.data == "main":
            inputs = keyboards_texts.continents()
            try:
                update.message.reply_text(inputs[0], reply_markup=inputs[1])
            except AttributeError:
                self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=inputs[0], reply_markup=inputs[1])
        elif query.data == "Antarctica":
            inputs = keyboards_texts.Antarctica()
            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=inputs[0], reply_markup=inputs[1])
        elif query.data in self.continents:
            nonsubscribed_countries = get_nonsubscribed_countries_by_continent(self.curr, telegram_id, query.data)
            inputs = keyboards_texts.countries(query.data, nonsubscribed_countries, telegram_id)
            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=inputs[0], reply_markup=inputs[1])
        elif query.data in all_countries:
            inputs = keyboards_texts.after_subscription(query.data)
            self.country_subscription(telegram_id, query.data)
            self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=inputs[0], reply_markup=inputs[1])
        else:
            self.unsubscribe(update,context)

    def unsubscribe(self, update, context):
        query = update.callback_query
        subscribed_countries = get_user_subscriptions(self.curr, update.effective_user.id)

        if query == None or query.data == "main_unsubscribe":
            inputs = keyboards_texts.subscribed_countries(subscribed_countries)
            try:
                update.message.reply_text(inputs[0], reply_markup=inputs[1])
            except AttributeError:
                self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=inputs[0], reply_markup=inputs[1])
        else:
            unsubscribed_country = query.data.replace("_unsubscribe", "")
            self.country_unsubscription(update.effective_user.id, unsubscribed_country)
            inputs = keyboards_texts.after_unsubscription(unsubscribed_country)
            try:
                self.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=inputs[0], reply_markup=inputs[1])
            except:
                update.message.reply_text(inputs[0], reply_markup=inputs[1])
                
    ''' 
    END OF COMMAND METHODS.
    '''

    def check_updates(self, context: telegram.ext.CallbackContext):
        check_new_country(self.conn, self.curr_job)
        country_list = get_all_countries(self.curr_job)

        for c in country_list:
            if check_if_updated(self.conn, self.curr_job, c) != False:
                users = get_users(self.curr_job)
                message_to_send = generate_update_message(c)
                for u in users:
                    if c == u[1]:
                        self.bot.send_message(chat_id=u[0], text=message_to_send)

    def country_subscription(self, user_id, query):
        save_user_subscription(self.conn, self.curr, user_id, query)

    def country_unsubscription(self, user_id, query):
        remove_user_subscription(self.conn, self.curr, user_id, query)

if __name__ == '__main__':
    bot = Bot()