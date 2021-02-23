from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from jobs import get_country_flag


def by_continent(continent, countries, callback_to):
    selected_continent_keyboard = []
    remainder = len(countries) % 3
    len_ = len(countries) if remainder == 0 else len(countries) - remainder

    for i in range(0, len_, 3):
        selected_continent_keyboard.append(
            [
                InlineKeyboardButton(
                    f"{countries[i]} {get_country_flag(countries[i])}",
                    callback_data=f"{callback_to}_{countries[i]}",
                ),
                InlineKeyboardButton(
                    f"{countries[i+1]} {get_country_flag(countries[i+1])}",
                    callback_data=f"{callback_to}_{countries[i+1]}",
                ),
                InlineKeyboardButton(
                    f"{countries[i+2]} {get_country_flag(countries[i+2])}",
                    callback_data=f"{callback_to}_{countries[i+2]}",
                ),
            ]
        )

    if remainder == 2:
        selected_continent_keyboard.append(
            [
                InlineKeyboardButton(
                    f"{countries[-2]} {get_country_flag(countries[-2])}",
                    callback_data=f"{callback_to}_{countries[-2]}",
                ),
                InlineKeyboardButton(
                    f"{countries[-1]} {get_country_flag(countries[-1])}",
                    callback_data=f"{callback_to}_{countries[-1]}",
                ),
            ]
        )
    elif remainder == 1:
        selected_continent_keyboard.append(
            [
                InlineKeyboardButton(
                    f"{countries[-1]} {get_country_flag(countries[-1])}",
                    callback_data=f"{callback_to}_{countries[-1]}",
                )
            ]
        )

    selected_continent_keyboard.append(
        [
            InlineKeyboardButton(
                "<< Back to continents menu", callback_data=f"{callback_to}_main"
            )
        ]
    )

    return f"Here is the list of the countries in {continent}", InlineKeyboardMarkup(
        selected_continent_keyboard
    )


def continents(callback_to):
    continents_keyboard = [
        [
            InlineKeyboardButton("Asia", callback_data=f"{callback_to}_Asia"),
            InlineKeyboardButton("Africa", callback_data=f"{callback_to}_Africa"),
        ],
        [
            InlineKeyboardButton(
                "North America", callback_data=f"{callback_to}_North America"
            ),
            InlineKeyboardButton(
                "South America", callback_data=f"{callback_to}_South America"
            ),
        ],
        [
            InlineKeyboardButton(
                "Antarctica", callback_data=f"{callback_to}_Antarctica"
            ),
            InlineKeyboardButton("Europe", callback_data=f"{callback_to}_Europe"),
        ],
        [InlineKeyboardButton("Oceania", callback_data=f"{callback_to}_Oceania")],
    ]

    return (
        "Please select the continent which the country you want choose to is in:",
        InlineKeyboardMarkup(continents_keyboard),
    )


def Antarctica(callback_to):
    selected_continent_keyboard = [
        [
            InlineKeyboardButton(
                "<< Back to continents menu", callback_data=f"{callback_to}_main"
            )
        ]
    ]

    return "Looks like no man's land.", InlineKeyboardMarkup(
        selected_continent_keyboard
    )


def after_subscription(country):
    subscribed_keyboard = [
        [
            InlineKeyboardButton(
                "<< Back to continents menu", callback_data="subscribe_main"
            )
        ]
    ]

    return f"You are successfully subscribed to {country}", InlineKeyboardMarkup(
        subscribed_keyboard
    )


def after_unsubscription(country):
    unsubscribed_keyboard = [
        [
            InlineKeyboardButton(
                "<< Back to unsubscription menu", callback_data="unsubscribe_main"
            )
        ]
    ]

    return f"{country} is unsubscribed", InlineKeyboardMarkup(unsubscribed_keyboard)


def github():
    github_keyboard = [
        [
            InlineKeyboardButton(
                "GitHub", url="https://github.com/memreyagci/covid-19-telegram-bot"
            )
        ]
    ]

    return (
        "Here is the GitHub repo of this bot. You can help me out by contributing and creating issues.",
        InlineKeyboardMarkup(github_keyboard),
    )


def subscribed(subscriptions):
    unsubscription_keyboard = []

    for i in subscriptions:
        unsubscription_keyboard.append(
            [
                InlineKeyboardButton(
                    f"{i} {get_country_flag(i)}", callback_data=f"unsubscribe_{i}"
                )
            ]
        )

    return (
        "Here are the countries you subscribed to.\nClick to unsubscribe.",
        InlineKeyboardMarkup(unsubscription_keyboard),
    )


def select_data(country):
    data_keyboard = []
    data = ["cases", "deaths", "recovered", "tests"]

    for i in range(0, len(data), 4):
        data_keyboard.append(
            [
                InlineKeyboardButton(data[i], callback_data=f"{country}_{data[i]}"),
                InlineKeyboardButton(
                    data[i + 1], callback_data=f"{country}_{data[i+1]}"
                ),
                InlineKeyboardButton(
                    data[i + 2], callback_data=f"{country}_{data[i+2]}"
                ),
                InlineKeyboardButton(
                    data[i + 3], callback_data=f"{country}_{data[i+3]}"
                ),
            ]
        )

    return "Please select which data you would like to know.", InlineKeyboardMarkup(
        data_keyboard
    )
