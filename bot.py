import logging
import os

import telegram
from telegram import ParseMode, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

import keyboards
import jobs
from database import Database

API = os.environ.get("CVBOT_API")
CONTINENTS = ["Asia", "Africa", "North America",
                "South America", "Antarctica", "Europe", "Oceania"]

class Bot:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

        self.database = Database()

        bot = telegram.Bot(token=API)
        updater = Updater(token=API)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('subscribe', self.subscribe))
        dispatcher.add_handler(CommandHandler('unsubscribe', self.unsubscribe))

        for continent in CONTINENTS:
            dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=continent))

        for i in self.database.get_all("name", "country"):
            dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern=i[0]))
            dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='{}_unsubscribe'.format(i[0])))

        dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern='main'))
        dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern='main_unsubscribe'))

        updater.start_polling()

        updater.job_queue.run_repeating(self.update_job, interval=900, first=10)

    def start(self, update, context):
        try:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                    text="Welcome to the COVID-19 Worldwide Statististics Bot!\n" \
                                        "You can access to the list of countries to subscribe via /subscribe command, " \
                                        "and to unsubscribe via /unsubscribe.\n To see this message again, " \
                                        "use the /start command. Command can also be seen via the / (slash) icon below, left of the attachments.")
            context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=keyboards.github()[0],
                                    reply_markup=keyboards.github()[1])
        except telegram.error.Unauthorized:
            self.database.delete_user(update.effective_chat.id)

    def subscribe(self, update, context):
        query = update.callback_query
        tid = update.effective_user.id
        countries = self.database.get_all("name", "country")

        if query is None or query.data == "main":
            inputs = keyboards.continents()
            try:
                update.message.reply_text(inputs[0], reply_markup=inputs[1])
            except AttributeError:
                context.bot.edit_message_text(chat_id=query.message.chat_id,
                                            message_id=query.message.message_id,
                                            text=inputs[0],
                                            reply_markup=inputs[1])
        elif query.data == "Antarctica":
            inputs = keyboards.Antarctica()
            context.bot.edit_message_text(chat_id=query.message.chat_id,
                                        message_id=query.message.message_id,
                                        text=inputs[0],
                                        reply_markup=inputs[1])
        elif query.data in CONTINENTS:
            nonsubscribed = self.database.get_nonsubscribed_by_continent(tid, query.data)
            inputs = keyboards.nonsubscribed_by_continent(query.data, nonsubscribed)
            context.bot.edit_message_text(chat_id=query.message.chat_id,
                                        message_id=query.message.message_id,
                                        text=inputs[0],
                                        reply_markup=inputs[1])
        elif query.data in countries:
            inputs = keyboards.after_subscription(query.data)
            self.database.save_subscription(tid, query.data)
            context.bot.edit_message_text(chat_id=query.message.chat_id,
                                        message_id=query.message.message_id,
                                        text=inputs[0],
                                        reply_markup=inputs[1])
        else:
            self.unsubscribe(update,context)

    def unsubscribe(self, update, context):
        query = update.callback_query
        subscriptions = self.database.get_where("subscription", "user",
                                                "tid", update.effective_user.id)

        if query is None or query.data == "main_unsubscribe":
            inputs = keyboards.subscribed(subscriptions)
            try:
                update.message.reply_text(inputs[0], reply_markup=inputs[1])
            except AttributeError:
                context.bot.edit_message_text(chat_id=query.message.chat_id,
                                            message_id=query.message.message_id,
                                            text=inputs[0],
                                            reply_markup=inputs[1])
        else:
            unsubscribed = query.data.replace("_unsubscribe", "")
            self.database.save_subscription(update.effective_user.id, unsubscribed)
            inputs = keyboards.after_unsubscription(unsubscribed)
            try:
                context.bot.edit_message_text(chat_id=query.message.chat_id,
                                            message_id=query.message.message_id,
                                            text=inputs[0],
                                            reply_markup=inputs[1])
            except:
                update.message.reply_text(inputs[0], reply_markup=inputs[1])

    def update_job(self, context):
        for country in self.database.get_all("name", "country"):
            updates = jobs.check_updates(
                    country,
                    self.database.get_where("cases", "country", "name", country)[0],
                    self.database.get_where("deaths", "country", "name", country)[0],
                    self.database.get_where("recovered", "country", "name", country)[0],
                    self.database.get_where("tests", "country", "name", country)[0]
                    )
            print(country)

            if updates is not False:
                if updates["cases"] != []:
                    self.database.update("country", "cases",
                            updates["cases"][0], "name", country)
                if updates["deaths"] != []:
                    self.database.update("country", "deaths",
                            updates["deaths"][0], "name", country)
                if updates["recovered"] != []:
                    self.database.update("country", "recovered",
                            updates["recovered"][0], "name", country)
                if updates["tests"] != []:
                    self.database.update("country", "tests",
                            updates["tests"][0], "name", country)

                users = self.database.get_users()
                message = jobs.generate_update_message(country, updates)
                for user in users:
                    if country == user[1]:
                        try:
                            context.bot.send_message(chat_id=user[0], text=message)
                        except telegram.error.Unauthorized:
                            self.database.delete_user(user[0])

if __name__ == '__main__':
    bot = Bot()
