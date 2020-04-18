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
        last_update_time text,
        country_stats json
        ); """
        )

def get_country_list(conn, curr):
    curr.execute("SELECT country_name FROM country")
    countries = curr.fetchall()
    countries_api = requests.get("https://corona.lmao.ninja/v2/countries").json()

    for i in range(len(countries_api)):
        if countries_api[i]["country"] not in countries:
            try:
                continent = pycountry_convert.convert_continent_code_to_continent_name(pycountry_convert.country_alpha2_to_continent_code(countries_api[i]["countryInfo"]["iso2"]))
                curr.execute("INSERT OR IGNORE INTO country (country_name, country_continent) VALUES (?,?)", (countries_api[i]["country"], continent,))
                conn.commit()
            except:
                pass
                
    curr.execute("SELECT country_name, country_continent FROM country")

    country_list = []

    for i in curr.fetchall():
        country_list.append(list(i))

    return country_list

def check_if_updated(conn, curr, country_name):
    curr.execute("""SELECT json(country_stats)
    FROM country WHERE country_name = ?""", (country_name,))

    req = requests.get("https://corona.lmao.ninja/countries/{}".format(country_name)).json()
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
            return new_stats
        else:
            return False

def get_users(curr):
    curr.execute("SELECT * FROM users")

    users_subscriptions = []

    for i in curr.fetchall():
        users_subscriptions.append(list(i))

    return users_subscriptions

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