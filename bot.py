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
    # The commands used in Telegram that starts with '/'. eg. /subscribe
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("get", get))

    # The first step of the commands
    dispatcher.add_handler(CallbackQueryHandler(subscribe, pattern="subscribe_main"))
    dispatcher.add_handler(
        CallbackQueryHandler(unsubscribe, pattern="unsubscribe_main")
    )
    dispatcher.add_handler(CallbackQueryHandler(get, pattern="get_main"))

    # Adding CallbackQueryHandlers to bring related countries after a continent button is clicked
    # in either subscribe or get menu
    for continent in CONTINENTS:
        dispatcher.add_handler(
            CallbackQueryHandler(subscribe, pattern=f"subscribe_{continent}")
        )
        dispatcher.add_handler(CallbackQueryHandler(get, pattern=f"get_{continent}"))

    # CallbackQueryHandlers of country button clicks, to subsribe, unsubscribe or show data selected
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
    """Default command that is run when a user starts a bot

    Raises:
        telegram.error.Unauthorized: If message cannot be sent, that means user no longer uses the bot, then delete their data.
    """
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

    # Show continents menu
    if query is None:
        continents_menu(update, context, query, "subscribe")
    else:
        query_data = query.data.split("_")[1]

        # Show continents menu
        if query_data == "main":
            continents_menu(update, context, query, "subscribe")
        # Show countries in selected continent
        elif query_data == "Antarctica":
            antarctica_menu(context, query, callback_to)
        elif query_data in CONTINENTS:
            with db.connection() as cursor:
                nonsubscribed = db.get_nonsubscribed_by_continent(
                    cursor, tid, query_data
                )
            countries_menu(context, query, query_data, nonsubscribed, callback_to)
        # Subscribe to selected country
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

    # Show nonsubscribed countries
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
    # Unsubscribe
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

    # Show continents menu
    if query is None:
        continents_menu(update, context, query, callback_to)
    else:
        query_data = query.data.split("_")[1]

        # Show continents menu
        if query_data == "main":
            continents_menu(update, context, query, callback_to)
        # Show countries in selected continent
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
        # Show type of data
        elif query_data in COUNTRIES:
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=texts.select_data(),
                reply_markup=keyboards.select_data(query_data),
            )
        # Show number of selected data
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
                    \nnumber of cases is {all_["cases"]:,},
                    \nnumber of deaths is {all_["deaths"]:,},
                    \nnumber of recovered is {all_["recovered"]:,},
                    \nand number of tests is {all_["tests"],}""",
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
        updates = jobs.check_updates(
            jobs.get_last_data(db.get(cursor, "*", "country", multiple=True)),
            jobs.get_current(),
        )

    for country in updates.keys():
        for data in updates[country].keys():
            if "difference" not in data and "today" not in data:
                with db.connection() as cursor:
                    db.update(
                        cursor,
                        "country",
                        data,
                        updates[country][data]["total"],
                        "name",
                        country,
                    )

    with db.connection() as cursor:
        users = db.get_users(cursor)

    messages = jobs.generate_update_message(updates)

    for user in users:
        if user[1] in messages.keys():
            try:
                context.bot.send_message(chat_id=user[0], text=messages[user[1]])
            except telegram.error.Unauthorized:
                with db.connection() as cursor:
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
