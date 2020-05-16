import os
from sqlalchemy import create_engine

import telegram
from telegram import ParseMode
from telegram.ext import CallbackContext, CommandHandler, Updater, CallbackQueryHandler
import logging

from get_information import generate_update_message, get_country_flag
from database import Database
import keyboards_texts

class Bot:
    def __init__(self):
        api = os.environ.get("CVBOT_API")
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

        self.database = Database()
        self.conn = self.database.get_connection()

        self.bot = telegram.Bot(token=api)
        self.updater = Updater(token=api, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('subscribe', self.subscribe))
        self.updater.dispatcher.add_handler(CommandHandler('unsubscribe', self.unsubscribe))

        self.continents = ["Asia", "Africa", "North America", "South America", "Antarctica", "Europe", "Oceania"]

        for i in self.continents:
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i))

        for i in self.database.check_new_country(self.conn):
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i[0]))
            self.updater.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='{}_unsubscribe'.format(i[0])))
        
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='main'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='main_unsubscribe'))

        self.updater.start_polling()

        print("started")

        update_job = self.updater.job_queue
        job_once = update_job.run_once(self.send_new_update_message, when=0)

        check_job = self.updater.job_queue
        job_minute = check_job.run_repeating(self.check_updates, interval=180, first=0)

    '''
    Methods of the commands (which are /start, /subscribe, and /unsubscribe so far.)
    '''

    def start(self, update, context):
        try:
            self.bot.send_message(chat_id=update.effective_chat.id, text=keyboards_texts.welcome_text())
            self.bot.send_message(chat_id=update.effective_chat.id, text=keyboards_texts.github()[0], reply_markup=keyboards_texts.github()[1])
        except telegram.error.Unauthorized:
            self.database.delete_user(self.conn, update.effective_chat.id)


    def subscribe(self, update, context):
        query = update.callback_query
        telegram_id = update.effective_user.id
        all_countries = self.database.get_all_countries(self.conn)
        
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
            nonsubscribed_countries = self.database.get_nonsubscribed_countries_by_continent(self.conn, telegram_id, query.data)
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
        subscribed_countries = self.database.get_user_subscriptions(self.conn, update.effective_user.id)

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
        self.database.check_new_country(self.conn)
        country_list = self.database.get_all_countries(self.conn)

        for c in country_list:
            if self.database.check_if_updated(self.conn, c) == True:
                users = self.database.get_users(self.conn)
                message_to_send = generate_update_message(c)
                for u in users:
                    if c == u[1]:
                        try:
                            self.bot.send_message(chat_id=u[0], text=message_to_send)
                        except telegram.error.Unauthorized:
                            self.database.delete_user(self.conn, u[0])

    def country_subscription(self, user_id, query):
        self.database.save_user_subscription(self.conn, user_id, query)

    def country_unsubscription(self, user_id, query):
        self.database.remove_user_subscription(self.conn, user_id, query)

    def send_new_update_message(self, context: telegram.ext.CallbackContext):
        new_update_message = open("update_message.txt", "r+")
        message_content = new_update_message.read()

        if message_content != '':
            users = self.database.get_user_ids(self.conn)
            for u in users:
                self.bot.send_message(chat_id=u, text=message_content, parse_mode=ParseMode.HTML)
            new_update_message.truncate(0)
        new_update_message.close()

if __name__ == '__main__':
    bot = Bot()