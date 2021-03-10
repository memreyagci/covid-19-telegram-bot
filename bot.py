import logging
import os

import telegram
from telegram.ext import CallbackQueryHandler, CommandHandler, Updater

import database as db
import jobs
import keyboards
import texts

API = os.environ.get("CVBOT_API")
CONTINENTS = [
    "Asia",
    "Africa",
    "North America",
    "South America",
    "Antarctica",
    "Europe",
    "Oceania",
]
DATA = ["cases", "deaths", "recovered", "tests", "all"]

with db.connection() as curr:
    COUNTRIES = db.get(curr, "name", "country")


def add_handlers():
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("get", get))

    dispatcher.add_handler(CallbackQueryHandler(subscribe, pattern="subscribe_main"))
    dispatcher.add_handler(
        CallbackQueryHandler(unsubscribe, pattern="unsubscribe_main")
    )
    dispatcher.add_handler(CallbackQueryHandler(get, pattern="get_main"))

    for continent in CONTINENTS:
        dispatcher.add_handler(
            CallbackQueryHandler(subscribe, pattern=f"subscribe_{continent}")
        )
        dispatcher.add_handler(CallbackQueryHandler(get, pattern=f"get_{continent}"))

    for country in COUNTRIES:
        dispatcher.add_handler(
            CallbackQueryHandler(subscribe, pattern=f"subscribe_{country}")
        )
        dispatcher.add_handler(
            CallbackQueryHandler(unsubscribe, pattern=f"unsubscribe_{country}")
        )
        dispatcher.add_handler(CallbackQueryHandler(get, pattern=f"get_{country}"))

        for data in DATA:
            dispatcher.add_handler(
                CallbackQueryHandler(get, pattern=f"{country}_{data}")
            )


def start(update, context):
    try:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=texts.welcome(),
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=texts.github(),
            reply_markup=keyboards.github(),
        )
    except telegram.error.Unauthorized:
        with db.connection() as cursor:
            db.delete_user(cursor, update.effective_chat.id)


def subscribe(update, context):
    query = update.callback_query
    tid = update.effective_user.id
    callback_to = "subscribe"

    if query is None:
        continents_menu(update, context, query, "subscribe")
    else:
        query_data = query.data.split("_")[1]

        if query_data == "main":
            continents_menu(update, context, query, "subscribe")
        elif query_data == "Antarctica":
            antarctica_menu(context, query, callback_to)
        elif query_data in CONTINENTS:
            with db.connection() as cursor:
                nonsubscribed = db.get_nonsubscribed_by_continent(
                    cursor, tid, query_data
                )

            countries_menu(context, query, query_data, nonsubscribed, callback_to)
        elif query_data in COUNTRIES:
            with db.connection() as cursor:
                db.save_subscription(cursor, tid, query_data)

            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=texts.after_subscription(query_data),
                reply_markup=keyboards.after_subscription(),
            )


def unsubscribe(update, context):
    query = update.callback_query

    with db.connection() as cursor:
        subscriptions = db.get(
            cursor, "subscription", "user", "tid", update.effective_user.id
        )

    if query is None or query.data == "unsubscribe_main":
        try:
            update.message.reply_text(
                texts.subscribed(), reply_markup=keyboards.subscribed(subscriptions)
            )
        except AttributeError:
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=texts.subscribed(),
                reply_markup=keyboards.subscribed(subscriptions),
            )
    else:
        unsubscribed = query.data.replace("unsubscribe_", "")

        with db.connection() as cursor:
            db.remove_subscription(cursor, update.effective_user.id, unsubscribed)

        try:
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=texts.after_unsubscription(unsubscribed),
                reply_markup=keyboards.after_unsubscription(),
            )
        except:
            update.message.reply_text(
                texts.after_subscription(unsubscribed),
                reply_markup=keyboards.after_subscription(),
            )


def get(update, context):
    query = update.callback_query
    callback_to = "get"

    if query is None:
        continents_menu(update, context, query, callback_to)
    else:
        query_data = query.data.split("_")[1]

        if query_data == "main":
            continents_menu(update, context, query, callback_to)
        elif query_data == "Antarctica":
            antarctica_menu(context, query, callback_to)
        elif query_data in CONTINENTS:

            with db.connection() as cursor:
                countries_by_continent = db.get(
                    cursor, "name", "country", "continent", query_data
                )

            countries_menu(
                context, query, query_data, countries_by_continent, callback_to
            )
        elif query_data in COUNTRIES:
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=texts.select_data(),
                reply_markup=keyboards.select_data(query_data),
            )
        else:
            country = query.data.split("_")[0]
            data = query.data.split("_")[1]

            if data == "all":
                all_ = {
                    "cases": None,
                    "deaths": None,
                    "recovered": None,
                    "tests": None,
                }
                for d in all_:
                    all_[d] = jobs.get_data(country, d)

                context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=f"""In {country},
                    \nnumber of cases is {all_["cases"]},
                    \nnumber of deaths is {all_["deaths"]},
                    \nnumber of recovered is {all_["recovered"]},
                    \nand number of tests is {all_["tests"]}""",
                )
            else:
                amount = jobs.get_data(country, data)
                context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=f"""Number of {data} in {country} is {amount}.""",
                )


def antarctica_menu(context, query, callback_to):
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=texts.antarctica(),
        reply_markup=keyboards.antarctica(callback_to),
    )


def countries_menu(context, query, continent, countries, callback_to):
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=texts.by_continent(continent),
        reply_markup=keyboards.by_continent(countries, callback_to),
    )


def continents_menu(update, context, query, callback_to):
    try:
        update.message.reply_text(
            texts.continents(), reply_markup=keyboards.continents(callback_to)
        )
    except AttributeError:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=texts.continents(),
            reply_markup=keyboards.continents(callback_to),
        )


def update_job(context):
    with db.connection() as cursor:
        for country in COUNTRIES:
            cases = db.get(cursor, "cases", "country", "name", country)[0]
            deaths = db.get(cursor, "deaths", "country", "name", country)[0]
            recovered = db.get(cursor, "recovered", "country", "name", country)[0]
            tests = db.get(cursor, "tests", "country", "name", country)[0]

            updates = jobs.check_updates(country, cases, deaths, recovered, tests)

            if isinstance(updates, dict):
                if updates["cases"] != []:
                    db.update(
                        cursor, "country", "cases", updates["cases"][0], "name", country
                    )
                if updates["deaths"] != []:
                    db.update(
                        cursor,
                        "country",
                        "deaths",
                        updates["deaths"][0],
                        "name",
                        country,
                    )
                if updates["recovered"] != []:
                    db.update(
                        cursor,
                        "country",
                        "recovered",
                        updates["recovered"][0],
                        "name",
                        country,
                    )
                if updates["tests"] != []:
                    db.update(
                        cursor, "country", "tests", updates["tests"][0], "name", country
                    )

                users = db.get_users(cursor)
                message = jobs.generate_update_message(country, updates)
                for user in users:
                    if country == user[1]:
                        try:
                            context.bot.send_message(chat_id=user[0], text=message)
                        except telegram.error.Unauthorized:
                            db.delete_user(cursor, user[0])


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    db.initialize_database()

    updater = Updater(token=API)
    dispatcher = updater.dispatcher

    add_handlers()

    updater.start_polling()
    updater.job_queue.run_repeating(update_job, interval=900, first=10)
    updater.idle()
