import requests
import pycountry_convert
import json

def create_tables(curr):
    curr.execute(
        """ CREATE TABLE IF NOT EXISTS user (
        telegram_id int,
        subscribed_country text
        ); """
        )

    curr.execute(
        """ CREATE TABLE IF NOT EXISTS country (
        country_name text UNIQUE,
        country_continent text,
        country_stats json
        ); """
        )

def check_new_country(conn, curr):
    countries = get_all_countries(curr)
    countries_api = requests.get("https://corona.lmao.ninja/v2/countries").json()

    for i in range(len(countries_api)):
        if countries_api[i]["country"] not in countries:
            try:
                continent = pycountry_convert.convert_continent_code_to_continent_name(pycountry_convert.country_alpha2_to_continent_code(countries_api[i]["countryInfo"]["iso2"]))
                curr.execute("INSERT OR IGNORE INTO country (country_name, country_continent) VALUES (?,?)", (countries_api[i]["country"], continent,))
                conn.commit()
            except:
                pass

    return get_all_countries(curr)

def get_all_countries(curr):
    curr.execute("SELECT country_name FROM country")

    all_countries = []

    for i in curr.fetchall():
        all_countries.append(i[0])

    return all_countries

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
            curr.execute("UPDATE country SET country_stats = ? WHERE country_name = ?", (json.dumps(new_stats), country_name,))
            conn.commit()
        else:
            if last_stats != new_stats:
                curr.execute("UPDATE country SET country_stats = ? WHERE country_name = ?", (json.dumps(new_stats), country_name,))
                conn.commit()
                return True
            else:
                return False

def get_users(curr):
    curr.execute("SELECT * FROM user")

    users_subscriptions = []

    for i in curr.fetchall():
        users_subscriptions.append(list(i))

    return users_subscriptions

def get_user_ids(curr):
    curr.execute("SELECT DISTINCT telegram_id FROM user")

    users_ids = []

    for i in curr.fetchall():
        users_ids.append(i[0])

    return users_ids

def get_user_subscriptions(curr, telegram_id):
    curr.execute("SELECT subscribed_country FROM user WHERE telegram_id = ?", (telegram_id,))

    subscription_list = []
    
    for i in curr.fetchall():
        subscription_list.append(list(i)[0])
    
    return subscription_list

def get_country_by_continent(curr, country_continent):
    curr.execute("SELECT country_name FROM country WHERE country_continent = ?", (country_continent,))

    country_list = []

    for i in curr.fetchall():
        country_list.append(list(i)[0])

    return country_list

def save_user_subscription(conn, curr, telegram_id, subscribed_country):
    curr.execute("INSERT OR IGNORE INTO user (telegram_id, subscribed_country) VALUES (?,?)", (telegram_id, subscribed_country,))
    conn.commit()

def remove_user_subscription(conn, curr, telegram_id, country_to_unsubscribe):
    curr.execute("DELETE FROM user WHERE telegram_id=? and subscribed_country=?", (telegram_id, country_to_unsubscribe,))
    conn.commit()

def get_nonsubscribed_countries_by_continent(curr, telegram_id, country_continent):
    curr.execute("SELECT country_name FROM country WHERE country_name NOT IN (SELECT subscribed_country FROM user WHERE telegram_id = ?) AND country_continent = ?", (telegram_id, country_continent,))

    nonsubscribed_countries = []

    for i in curr.fetchall():
        nonsubscribed_countries.append(i[0])

    return nonsubscribed_countries
