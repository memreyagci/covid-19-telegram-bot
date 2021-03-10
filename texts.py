def github():
    return "Here is the GitHub repo of this bot. You can help me out by contributing or creating issues."


def welcome():
    return (
        "Welcome to the COVID-19 Worldwide Statististics Bot!\n"
        "You can access to the list of countries to subscribe via /subscribe command, "
        "and to unsubscribe via /unsubscribe.\n To see this message again, "
        "use the /start command. Command can also be seen via the / (slash) icon below, left of the attachments."
    )


def after_subscription(country):
    return f"You are successfully subscribed to {country}"


def after_unsubscription(country):
    return f"{country} is unsubscribed"


def subscribed():
    return "Here are the subscriptions.\nClick to unsubscribe."


def select_data():
    return "Please select a data."


def antarctica():
    return "Looks like no man's land."


def by_continent(continent):
    return f"Here are the countries in {continent}"


def continents():
    return "Please select a continent:"
