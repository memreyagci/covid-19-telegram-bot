from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from jobs import get_country_flag

def by_continent(continent, countries, callback_to):
    selected_continent_keyboard = []

    for i in range(0, len(countries), 3):
        try:
            selected_continent_keyboard.append([
            InlineKeyboardButton("{} {}".format(countries[i],
                                                get_country_flag(countries[i])),
                                                callback_data="{}_{}"
                                                .format(callback_to, countries[i])),
            InlineKeyboardButton("{} {}".format(countries[i+1],
                                                get_country_flag(countries[i+1])),
                                                callback_data="{}_{}"
                                                .format(callback_to, countries[i+1])),
            InlineKeyboardButton("{} {}".format(countries[i+2],
                                                get_country_flag(countries[i+2])),
                                                callback_data="{}_{}"
                                                .format(callback_to, countries[i+2]))
                    ])
        except:
            try:
                selected_continent_keyboard.append([
            InlineKeyboardButton("{} {}".format(countries[i],
                                                get_country_flag(countries[i])),
                                                callback_data="{}_{}"
                                                .format(callback_to, countries[i])),
            InlineKeyboardButton("{} {}".format(countries[i+1],
                                                get_country_flag(countries[i+1])),
                                                callback_data="{}_{}"
                                                .format(callback_to, countries[i+1]))
                ])
            except:
                selected_continent_keyboard.append([
            InlineKeyboardButton("{} {}".format(countries[i],
                                                get_country_flag(countries[i])),
                                                callback_data="{}_{}"
                                                .format(callback_to, countries[i]))
                ])

    selected_continent_keyboard.append([
        InlineKeyboardButton("<< Back to continents menu",
            callback_data="{}_main".format(callback_to))
            ])

    return "Here is the list of the countries in {}".format(continent), InlineKeyboardMarkup(selected_continent_keyboard)

def continents(callback_to):
    continents_keyboard =[
        [
            InlineKeyboardButton("Asia", callback_data="{}_Asia".format(callback_to)),
            InlineKeyboardButton("Africa", callback_data="{}_Africa".format(callback_to))
                ],
        [
            InlineKeyboardButton("North America", callback_data="{}_North America".format(callback_to)),
            InlineKeyboardButton("South America", callback_data="{}_South America".format(callback_to))
                ],
        [
            InlineKeyboardButton("Antarctica", callback_data="{}_Antarctica".format(callback_to)),
            InlineKeyboardButton("Europe", callback_data="{}_Europe".format(callback_to))
                ],
        [
            InlineKeyboardButton("Oceania", callback_data="{}_Oceania".format(callback_to))
                ]
    ]

    return "Please select the continent which the country you want choose to is in:", InlineKeyboardMarkup(continents_keyboard)

def Antarctica(callback_to):
    selected_continent_keyboard= [
       [ InlineKeyboardButton("<< Back to continents menu", callback_data="{}_main".format(callback_to)) ]
            ]

    return "Looks like no man's land.", InlineKeyboardMarkup(selected_continent_keyboard)

def after_subscription(country):
    subscribed_keyboard = [
            [InlineKeyboardButton("<< Back to continents menu", callback_data="subscribe_main")]
            ]

    return "You are successfully subscribed to {}".format(country), InlineKeyboardMarkup(subscribed_keyboard)

def after_unsubscription(country):
    unsubscribed_keyboard = [
            [InlineKeyboardButton("<< Back to unsubscription menu", callback_data="unsubcribe_main")]
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
        print (i)
        unsubscription_keyboard.append([
            InlineKeyboardButton('{} {}'
                .format(i, get_country_flag(i)), callback_data='{}_unsubscribe'.format(i))
                ])

    return "Here are the countries you subscribed to.\nClick to unsubscribe.", InlineKeyboardMarkup(unsubscription_keyboard)

def select_data(country):
    data_keyboard = []
    data = ["cases", "deaths", "recovered", "tests"]

    for i in range(0, len(data), 4):
        data_keyboard.append([
             InlineKeyboardButton(data[i], callback_data="{}_{}".format(country, data[i])),
             InlineKeyboardButton(data[i+1], callback_data="{}_{}".format(country, data[i+1])),
             InlineKeyboardButton(data[i+2], callback_data="{}_{}".format(country, data[i+2])),
             InlineKeyboardButton(data[i+3], callback_data="{}_{}".format(country, data[i+3]))
            ])

    return "Please select which data you would like to know.", InlineKeyboardMarkup(data_keyboard)
