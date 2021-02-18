import json
import requests
import pycountry_convert
import mysql.connector
from mysql.connector import Error
import config

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                    host=config.mysql["host"],
                    database=config.mysql["database"],
                    user=config.mysql["user"],
                    password=config.mysql["password"])
            self.conn.autocommit=True
        except Error as e:
            print(e)

        self.cursor = self.conn.cursor(buffered=True)

        self.create_tables()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user (tid int NOT NULL, subscription VARCHAR(255))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS country " \
                                "(name VARCHAR(255) NOT NULL UNIQUE, " \
                                "continent VARCHAR(255) NOT NULL, " \
                                "stats JSON)")

    def get_all(self, column, table):
        all_ = []
        self.cursor.execute("SELECT {} FROM {}".format(column, table))

        try:
            for row in self.cursor.fetchall():
                all_.append(row[0])
            return all_
        except:
            return []

    def get_users(self):
        users_subscriptions = []
        self.cursor.execute("SELECT * FROM users")

        for row in self.cursor.fetchall():
            users_subscriptions.append(list(row))

        return users_subscriptions

    def get_where(self, column, table, where1, where2):
        list_ = []
        self.cursor.execute("SELECT {} FROM {} WHERE {} = {}".format(column, table, where1, where2))

        for row in self.cursor.fetchall():
            list_.append(list(row)[0])

        return list_

    def check_new_country(self):
        countries = self.get_all("name", "country")
        try:
            countries_api = requests.get("https://corona.lmao.ninja/v2/countries").json()
        except json.decoder.JSONDecodeError: #To prevent crashing of bot.py in case of Error 502 of corona.lmao.ninja
            pass
        else:
            for i in range(len(countries_api)):
                if countries_api[i]["country"] not in countries:
                    try:
                        continent = pycountry_convert.convert_continent_code_to_continent_name(
                                pycountry_convert.country_alpha2_to_continent_code(countries_api[i]["countryInfo"]["iso2"]))
                        self.cursor.execute("INSERT IGNORE INTO country(name, continent) VALUES (%s, %s)",
                                            (countries_api[i]["country"], continent))
                    except:
                        pass

            return self.get_all("name", "country")

    def check_if_updated(self, country):
        try:
            req = requests.get("https://corona.lmao.ninja/v2/countries/{}".format(country)).json()
        except ConnectionError:
            pass
        else:
            new_stats = [req["cases"] , req["deaths"], req["recovered"] ,
                        req["active"], req["critical"] , req["tests"]]

            try:
                self.cursor.execute("SELECT stats FROM country WHERE country.name = %s", (country))
                last_stats = json.loads(self.cursor.fetchone()[0])
            except:
                self.cursor.execute("UPDATE country SET stats = %s " \
                                    "WHERE name = %s", (json.dumps(new_stats), country))
            else:
                if last_stats != new_stats:
                    self.cursor.execute("UPDATE country SET stats = %s " \
                                        "WHERE country.name = %s",
                                        (json.dumps(new_stats), country))
                    return True
                else:
                    return False

    def save_subscription(self, tid, subscription):
        self.cursor.execute("INSERT INTO user (tid, subscription)" \
                            "VALUES (%s, %s)", (tid, subscription))

    def remove_subscription(self, tid, subscription):
        self.cursor.execute("DELETE FROM user WHERE tid = %s AND subscription = %s",
                            (tid, subscription))

    def get_nonsubscribed_by_continent(self, tid, continent):
        nonsubscribed = []

        try:
            self.cursor.execute("SELECT name FROM country WHERE name NOT IN " \
                                "(SELECT subscription FROM user WHERE tid = %s) AND " \
                                "continent = %s", (tid, continent))
            for row in self.cursor.fetchall():
                nonsubscribed.append(row[0])

            return nonsubscribed
        except AttributeError:
            return self.get_all("name", "country")

    def delete_user(self, tid):
        self.cursor.execute("DELETE FROM user WHERE tid = %s", (tid))
