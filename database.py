import json
import jobs
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
                password=config.mysql["password"],
            )
            self.conn.autocommit = True
        except Error as e:
            print(e)

        self.cursor = self.conn.cursor(buffered=True)

        self.create_tables()
        self.initialize_countries()

    def create_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS user (tid int NOT NULL, subscription VARCHAR(255))"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS country "
            "(name VARCHAR(255) NOT NULL UNIQUE, "
            "continent VARCHAR(255) NOT NULL, "
            "cases int, "
            "deaths int, "
            "recovered int, "
            "tests int)"
        )

    def get_all(self, column, table):
        all_ = []
        self.cursor.execute(f"SELECT {column} FROM {table}")

        try:
            for row in self.cursor.fetchall():
                all_.append(row[0])
            return all_
        except:
            return []

    def get_users(self):
        users_subscriptions = []
        self.cursor.execute("SELECT * FROM user")

        for row in self.cursor.fetchall():
            users_subscriptions.append(list(row))

        return users_subscriptions

    def get_where(self, column, table, where1, where2):
        list_ = []
        self.cursor.execute(f'SELECT {column} FROM {table} WHERE {where1} = "{where2}"')

        for row in self.cursor.fetchall():
            list_.append(list(row)[0])

        return list_

    def update(self, table, column, set_, where1, where2):
        self.cursor.execute(
            f'UPDATE {table} SET {column} = {set_} WHERE {where1} = "{where2}"'
        )

    def initialize_countries(self):
        countries = self.get_all("name", "country")
        try:
            data = jobs.fetch_data()
        except json.decoder.JSONDecodeError:  # To prevent crashing of bot.py in case of Error 502 of corona.lmao.ninja
            pass
        else:
            for i in range(len(data)):
                if data[i]["country"] not in countries:
                    try:
                        continent = (
                            pycountry_convert.convert_continent_code_to_continent_name(
                                pycountry_convert.country_alpha2_to_continent_code(
                                    data[i]["countryInfo"]["iso2"]
                                )
                            )
                        )
                        self.cursor.execute(
                            "INSERT IGNORE INTO country(name, continent, cases, deaths, recovered, tests) "
                            "VALUES (%s, %s, %s, %s, %s, %s)",
                            (
                                data[i]["country"],
                                continent,
                                data[i]["cases"],
                                data[i]["deaths"],
                                data[i]["recovered"],
                                data[i]["tests"],
                            ),
                        )
                    except:
                        pass

    def save_subscription(self, tid, subscription):
        self.cursor.execute(
            "INSERT INTO user (tid, subscription)" "VALUES (%s, %s)",
            (tid, subscription),
        )

    def remove_subscription(self, tid, subscription):
        self.cursor.execute(
            "DELETE FROM user WHERE tid = %s AND subscription = %s", (tid, subscription)
        )

    def get_nonsubscribed_by_continent(self, tid, continent):
        nonsubscribed = []

        try:
            self.cursor.execute(
                "SELECT name FROM country WHERE name NOT IN "
                "(SELECT subscription FROM user WHERE tid = %s) AND "
                "continent = %s",
                (tid, continent),
            )
            for row in self.cursor.fetchall():
                nonsubscribed.append(row[0])

            return nonsubscribed
        except AttributeError:
            return self.get_all("name", "country")

    def delete_user(self, tid):
        self.cursor.execute("DELETE FROM user WHERE tid = %s", (tid))
