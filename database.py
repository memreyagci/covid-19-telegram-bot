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
    countries_api = requests.get("https://corona.lmao.ninja/countries").json()

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
    curr.execute("SELECT last_update_time FROM country WHERE country_name = ?", (country_name,))

    last_update_time = int(list(curr.fetchone())[0])
    new_update_time = requests.get("https://corona.lmao.ninja/countries/{}".format(country_name)).json()["updated"]

    if last_update_time != new_update_time:
        curr.execute("UPDATE country SET last_update_time = ? WHERE country_name = ?", (str(new_update_time), country_name,))
        conn.commit()
        return str(new_update_time)
    else:
        return False

def check_if_updated2(conn, curr, country_name):
    # curr.execute("""SELECT json_extract(country_stats,
    # '$.cases', '$.todayCases', '$.deaths', '$.todayDeaths', '$.recovered', '$.active', '$.critical', '$.casesPerOneMillion', '$.deathsPerOneMillion', '$.tests', '$.testsPerOneMillion')
    # FROM country WHERE country_name = ?""", (country_name,))

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
            print(last_stats)
            print(new_stats)
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

    return list(curr.fetchall())

def save_user_subcsription(curr, conn, telegram_id, country_name):
    curr.execute("INSERT OR IGNORE INTO user (telegram_id, country_name) VALUES (?,?)", (telegram_id, country_name,))
    conn.commit()