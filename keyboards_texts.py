from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from get_information import get_country_flag

def countries(continent, nonsubscribed_countries, telegram_id):
    selected_continent_keyboard = []

    for i in range(0, len(nonsubscribed_countries), 3):
            try:
                selected_continent_keyboard.append([
                InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i], get_country_flag(nonsubscribed_countries[i])), callback_data=nonsubscribed_countries[i]),
                InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i+1], get_country_flag(nonsubscribed_countries[i+1])), callback_data=nonsubscribed_countries[i+1]),
                InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i+2], get_country_flag(nonsubscribed_countries[i+2])), callback_data=nonsubscribed_countries[i+2])
                        ])
            except:
                try:
                    selected_continent_keyboard.append([
                InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i], get_country_flag(nonsubscribed_countries[i])), callback_data=nonsubscribed_countries[i]),
                InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i+1], get_country_flag(nonsubscribed_countries[i+1])), callback_data=nonsubscribed_countries[i+1])
                    ])
                except:
                    selected_continent_keyboard.append([
                InlineKeyboardButton("{} {}".format(nonsubscribed_countries[i], get_country_flag(nonsubscribed_countries[i])), callback_data=nonsubscribed_countries[i])
                    ])

    selected_continent_keyboard.append([
        InlineKeyboardButton("<< Back to continents menu", callback_data="main")
            ])

    return "Here is the list of the countries in {}".format(continent), InlineKeyboardMarkup(selected_continent_keyboard)


def continents():
    continents_keyboard =[
        [
            InlineKeyboardButton("Asia", callback_data="Asia"),
            InlineKeyboardButton("Africa", callback_data="Africa")
                ],
        [
            InlineKeyboardButton("North America", callback_data="North America"),
            InlineKeyboardButton("South America", callback_data="South America")
                ],
        [
            InlineKeyboardButton("Antarctica", callback_data="Antarctica"),
            InlineKeyboardButton("Europe", callback_data="Europe")
                ],
        [
            InlineKeyboardButton("Oceania", callback_data="Oceania")
                ]
    ]

    return "Please select the continent which the country you want subscribe to is in:", InlineKeyboardMarkup(continents_keyboard)


def Antarctica():
    selected_continent_keyboard= [
        InlineKeyboardButton("<< Back to continents menu", callback_data="main")
            ]

    return "Looks like no man's land.", InlineKeyboardMarkup(selected_continent_keyboard)


def after_subscription(country):
    subscribed_keyboard = [[InlineKeyboardButton("<< Back to continents menu", callback_data="main")]]
    
    return "You are successfully subscribed to {}".format(country), InlineKeyboardMarkup(subscribed_keyboard)


def after_unsubscription(country):
    unsubscribed_keyboard = [[InlineKeyboardButton("<< Back to unsubscription menu", callback_data="main_unsubscribe")]]

    return "{} is unsubscribed".format(country), InlineKeyboardMarkup(unsubscribed_keyboard)


def welcome_text():
    return "Welcome to the COVID-19 Worldwide Statististics Bot!\nYou can access to the list of countries to subscribe via /subscribe command, and to unsubscribe via /unsubscribe.\nTo see this message again, use the /start command. Command can also be seen via the / (slash) icon below, left of the attachments."


def github():
    github_keyboard = [[InlineKeyboardButton("GitHub", url='https://github.com/memreyagci/covid-19-telegram-bot')]]

    return "Here is the GitHub repo of this bot. You can help me out by contributing and creating issues.", InlineKeyboardMarkup(github_keyboard)


def subscribed_countries(subscribed_countries):
    unsubscription_keyboard = []

    for i in subscribed_countries:
        unsubscription_keyboard.append([
            InlineKeyboardButton('{} {}'.format(i, get_country_flag(i)), callback_data='{}_unsubscribe'.format(i))
                ])

    return "Here are the countries you subscribed to.\nClick to unsubscribe.", InlineKeyboardMarkup(unsubscription_keyboard)