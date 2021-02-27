import json
import jobs
import requests
import pycountry_convert
import mysql.connector
from mysql.connector import Error
import config
from contextlib import contextmanager


@contextmanager
def connection():
    try:
        conn = mysql.connector.connect(
            host=config.mysql["host"],
            database=config.mysql["database"],
            user=config.mysql["user"],
            password=config.mysql["password"],
        )
    except Error as e:
        print(e)
    else:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
        conn.close()


def get_all(cursor, column, table):
    all_ = []
    cursor.execute(f"SELECT {column} FROM {table}")

    try:
        for row in cursor.fetchall():
            all_.append(row[0])
        return all_
    except:
        return []


def get_users(cursor):
    users_subscriptions = []
    cursor.execute("SELECT * FROM user")

    for row in cursor.fetchall():
        users_subscriptions.append(list(row))

    return users_subscriptions


def get_where(cursor, column, table, where1, where2):
    list_ = []
    cursor.execute(f'SELECT {column} FROM {table} WHERE {where1} = "{where2}"')

    for row in cursor.fetchall():
        list_.append(list(row)[0])

    return list_


def update(cursor, table, column, set_, where1, where2):
    cursor.execute(f'UPDATE {table} SET {column} = {set_} WHERE {where1} = "{where2}"')


def save_subscription(cursor, tid, subscription):
    cursor.execute(
        "INSERT INTO user (tid, subscription)" "VALUES (%s, %s)",
        (tid, subscription),
    )


def remove_subscription(cursor, tid, subscription):
    cursor.execute(
        "DELETE FROM user WHERE tid = %s AND subscription = %s", (tid, subscription)
    )


def get_nonsubscribed_by_continent(cursor, tid, continent):
    nonsubscribed = []

    try:
        cursor.execute(
            "SELECT name FROM country WHERE name NOT IN "
            "(SELECT subscription FROM user WHERE tid = %s) AND "
            "continent = %s",
            (tid, continent),
        )
        for row in cursor.fetchall():
            nonsubscribed.append(row[0])

        return nonsubscribed
    except AttributeError:
        return get_all(cursor, "name", "country")


def delete_user(cursor, tid):
    cursor.execute("DELETE FROM user WHERE tid = %s", (tid))


def initialize_database():
    with connection() as cursor:
        create_tables(cursor)
        initialize_countries(cursor)


def create_tables(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (tid int NOT NULL, subscription VARCHAR(255))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS country "
        "(name VARCHAR(255) NOT NULL UNIQUE, "
        "continent VARCHAR(255) NOT NULL, "
        "cases int, "
        "deaths int, "
        "recovered int, "
        "tests int)"
    )


def initialize_countries(cursor):
    countries = get_all(cursor, "name", "country")
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
                    cursor.execute(
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
