import requests
import pycountry_convert
import json
from sqlalchemy import create_engine, MetaData

def create_engine_and_connection():
    engine = create_engine('sqlite:///covid19.db', echo = True)

    return engine, engine.connect()

def create_tables(engine):
    meta = MetaData()

    user = Table(
        'user', meta,
        Column('telegram_id', Integer),
        Column('subscribed_country', String)
    )
    country = Table(
        'country', meta,
        Column('country_name', String),
        Column('country_continent', String, unique=True),
        Column('country_stats', JSON)
    )
    
    meta.create_all(engine)

def get_all_countries(conn):
    statement = select([country.country_name])
    all_countries = []

    for i in conn.execute(statement):
        all_countries.append(i[0])

    return all_countries

def get_users(conn):
    statement = select(user)
    users_subscriptions = []

    for i in conn.execute(statement):
        users_subscriptions.append(list(i))

    return users_subscriptions

def get_user_ids(conn):
    statement = select([user.telegram_id.distinct()])
    users_ids = []

    for i in conn.execute(statement):
        users_ids.append(i[0])

    return users_ids

def get_user_subscriptions(conn, telegram_id):
    statement = select([user.subscribed_country]).where(user.telegram_id == telegram_id)
    subscription_list = []
    
    for i in conn.execute(statement):
        subscription_list.append(list(i)[0])
    
    return subscription_list

def get_country_by_continent(conn, country_continent):
    statement = select([country.country_name]).where(country.country_continent == country_continent)
    country_list = []

    for i in conn.execute(statement):
        country_list.append(list(i)[0])

    return country_list

def check_new_country(conn):
    countries = get_all_countries(curr)

    try:
        countries_api = requests.get("https://corona.lmao.ninja/v2/countries").json()
    except json.decoder.JSONDecodeError: #To prevent crashing of bot.py in case of Error 502 of corona.lmao.ninja
        pass
    else:
        for i in range(len(countries_api)):
            if countries_api[i]["country"] not in countries:
                try:
                    continent = pycountry_convert.convert_continent_code_to_continent_name(pycountry_convert.country_alpha2_to_continent_code(countries_api[i]["countryInfo"]["iso2"]))
                    statement = country.insert().values(country_name=countries_api[i]["country"], country_continent=continent)
                    conn.execute(statement)
                except:
                    pass

        return get_all_countries(curr)

def check_if_updated(conn, curr, country_name):
    curr.execute("""SELECT json(country_stats)
    FROM country WHERE country_name = ?""", (country_name,))

    try:
        req = requests.get("https://corona.lmao.ninja/v2/countries/{}".format(country_name)).json()
    except:
        pass
    else:
        new_stats = [req["cases"] , req["deaths"], req["recovered"] , req["active"], req["critical"] , req["tests"]]

        try:
            last_stats = json.loads(curr.fetchone()[0])
        except:
            statement = country.update().where(country.country_name == country_name).values(country_stats = json.dumps(new_stats))
            conn.execute(statement)
        else:
            if last_stats != new_stats:
                statement = country.update().where(country.country_name == country_name).values(country_stats = json.dumps(new_stats))
                conn.execute(statement)
                return True
            else:
                return False

def save_user_subscription(conn, curr, telegram_id, subscribed_country):
    statement = user.insert().values(telegram_id=telegram_id, subscribed_country=subscribed_country)
    conn.execute(statement)

def remove_user_subscription(conn, telegram_id, country_to_unsubscribe):
    statement = user.delete().where(user.telegram_id == telegram_id, user.subscribed_country == country_to_unsubscribe)
    conn.execute(statement)

def get_nonsubscribed_countries_by_continent(curr, telegram_id, country_continent):
    statement1 = select([user.subscribed_country]).where(user.telegram_id == telegram_id)
    statement2 = select([country.country_name]).where(country.country_name.)
    curr.execute("SELECT country_name FROM country WHERE country_name NOT IN (SELECT subscribed_country FROM user WHERE telegram_id = ?) AND country_continent = ?", (telegram_id, country_continent,))

    nonsubscribed_countries = []

    for i in curr.fetchall():
        nonsubscribed_countries.append(i[0])

    return nonsubscribed_countries

def delete_user(conn,, telegram_id):
    statement = user.delete().where(user.telegram_id == telegram_id)
    conn.execute(statement)
