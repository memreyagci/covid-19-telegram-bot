from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from get_information import get_country_flag

def nonsubscribed_by_continent(continent, nonsubscribed):
    selected_continent_keyboard = []

    for i in range(0, len(nonsubscribed), 3):
        try:
            selected_continent_keyboard.append([
            InlineKeyboardButton("{} {}".format(nonsubscribed[i],
                                                get_country_flag(nonsubscribed[i])),
                                                callback_data=nonsubscribed[i]),
            InlineKeyboardButton("{} {}".format(nonsubscribed[i+1],
                                                get_country_flag(nonsubscribed[i+1])),
                                                callback_data=nonsubscribed[i+1]),
            InlineKeyboardButton("{} {}".format(nonsubscribed[i+2],
                                                get_country_flag(nonsubscribed[i+2])),
                                                callback_data=nonsubscribed[i+2])
                    ])
        except:
            try:
                selected_continent_keyboard.append([
            InlineKeyboardButton("{} {}".format(nonsubscribed[i],
                                                get_country_flag(nonsubscribed[i])),
                                                callback_data=nonsubscribed[i]),
            InlineKeyboardButton("{} {}".format(nonsubscribed[i+1],
                                                get_country_flag(nonsubscribed[i+1])),
                                                callback_data=nonsubscribed[i+1])
                ])
            except:
                selected_continent_keyboard.append([
            InlineKeyboardButton("{} {}".format(nonsubscribed[i],
                                                get_country_flag(nonsubscribed[i])),
                                                callback_data=nonsubscribed[i])
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
       [ InlineKeyboardButton("<< Back to continents menu", callback_data="main") ]
            ]

    return "Looks like no man's land.", InlineKeyboardMarkup(selected_continent_keyboard)


def after_subscription(country):
    subscribed_keyboard = [
            [InlineKeyboardButton("<< Back to continents menu", callback_data="main")]
            ]

    return "You are successfully subscribed to {}".format(country), InlineKeyboardMarkup(subscribed_keyboard)


def after_unsubscription(country):
    unsubscribed_keyboard = [
            [InlineKeyboardButton("<< Back to unsubscription menu", callback_data="main_unsubscribe")]
            ]

    return "{} is unsubscribed".format(country), InlineKeyboardMarkup(unsubscribed_keyboard)

def github():
    github_keyboard = [
            [InlineKeyboardButton("GitHub", url='https://github.com/memreyagci/covid-19-telegram-bot')]
            ]

    return "Here is the GitHub repo of this bot. You can help me out by contributing and creating issues.", InlineKeyboardMarkup(github_keyboard)


def subscribed(subscriptions):
    unsubscription_keyboard = []

    for i in subscriptions:
        unsubscription_keyboard.append([
            InlineKeyboardButton('{} {}'
                .format(i, get_country_flag(i)), callback_data='{}_unsubscribe'.format(i))
                ])

    return "Here are the countries you subscribed to.\nClick to unsubscribe.", InlineKeyboardMarkup(unsubscription_keyboard)
