from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from jobs import get_country_flag


def by_continent(continent, countries, callback_to):
    keyboard = []
    remainder = len(countries) % 3
    len_ = len(countries) if remainder == 0 else len(countries) - remainder

    for i in range(0, len_, 3):
        keyboard.append(
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
        keyboard.append(
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
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{countries[-1]} {get_country_flag(countries[-1])}",
                    callback_data=f"{callback_to}_{countries[-1]}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                "<< Back to continents menu", callback_data=f"{callback_to}_main"
            )
        ]
    )

    return f"Here are the countries in {continent}", InlineKeyboardMarkup(keyboard)


def continents(callback_to):
    keyboard = [
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
        "Please select a continent:",
        InlineKeyboardMarkup(keyboard),
    )


def Antarctica(callback_to):
    keyboard = [
        [
            InlineKeyboardButton(
                "<< Back to continents", callback_data=f"{callback_to}_main"
            )
        ]
    ]

    return "Looks like no man's land.", InlineKeyboardMarkup(keyboard)


def after_subscription(country):
    keyboard = [
        [InlineKeyboardButton("<< Back to continents", callback_data="subscribe_main")]
    ]

    return f"You are successfully subscribed to {country}", InlineKeyboardMarkup(
        keyboard
    )


def after_unsubscription(country):
    keyboard = [
        [
            InlineKeyboardButton(
                "<< Back to unsubscriptions", callback_data="unsubscribe_main"
            )
        ]
    ]

    return f"{country} is unsubscribed", InlineKeyboardMarkup(keyboard)


def github():
    keyboard = [
        [
            InlineKeyboardButton(
                "GitHub", url="https://github.com/memreyagci/covid-19-telegram-bot"
            )
        ]
    ]

    return (
        "Here is the GitHub repo of this bot. You can help me out by contributing or creating issues.",
        InlineKeyboardMarkup(keyboard),
    )


def subscribed(subscriptions):
    unkeyboard = []

    for i in subscriptions:
        unkeyboard.append(
            [
                InlineKeyboardButton(
                    f"{i} {get_country_flag(i)}", callback_data=f"unsubscribe_{i}"
                )
            ]
        )

    return (
        "Here are the subscriptions.\nClick to unsubscribe.",
        InlineKeyboardMarkup(unkeyboard),
    )


def select_data(country):
    keyboard = []
    data = ["cases", "deaths", "recovered", "tests"]

    for i in range(0, len(data), 4):
        keyboard.append(
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

    keyboard.append([InlineKeyboardButton("all", callback_data=f"{country}_all")])

    return "Please select a data.", InlineKeyboardMarkup(keyboard)
