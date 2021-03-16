from contextlib import contextmanager
import json
import os

import mysql.connector
from mysql.connector import Error
import pycountry_convert

import jobs


@contextmanager
def connection():
    """A context manager to be used in CRUD operations.

    Returns:
        :obj:`mysql.connector.cursor.MySQLCursor`

    """
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST"),
            database=os.environ.get("MYSQL_DB"),
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
        )
    except Error as e:
        print(e)
    else:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
        conn.close()


def get(cursor, column, table, where1=None, where2=None, multiple=False) -> list:
    """Fetches data from the database

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor
        column (str): The column to be selected
        table (str): The table to select from
        where1 (str, optional): (see where2)
        where2 (str, optional): To be used with where1. Let's you define a condition for selection

    Returns:
        list: fetched data, [] if empty

    """
    result = []
    statement = f"SELECT {column} FROM {table}"
    statement += f' WHERE {where1} = "{where2}"' if where1 is not None else ""

    cursor.execute(statement)

    try:
        for row in cursor.fetchall():
            result.append(row[0]) if multiple == False else result.append(row)
        return result
    except:
        return []


def get_users(cursor) -> list:
    """Returns pairs of Telegram IDs and subscribed country names.

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor

    Returns:
        list(list(int, str)): pair of Telegram IDs (int) and subscribed country name (string)

    """
    users_subscriptions = []
    cursor.execute("SELECT * FROM user")

    for row in cursor.fetchall():
        users_subscriptions.append(list(row))

    return users_subscriptions


def update(cursor, table, column, set_, where1, where2):
    """A wrapper function for UPDATE command of SQL

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor
        table (str): Table to be updated
        column (str): Column(s) to be updated
        set_ (str): New value(s)
        where1 (str, optional): (see where2)
        where2 (str, optional): To be used with where1. Let's you define a condition for selection

    """
    cursor.execute(f'UPDATE {table} SET {column} = {set_} WHERE {where1} = "{where2}"')


def save_subscription(cursor, tid, subscription):
    """A wrapper function for INSERT command of SQL
    j
    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor
        tid (int): Telegram ID of the user subscribing
        subscription (str): Country name to subscribe

    """
    cursor.execute(
        "INSERT INTO user (tid, subscription)" "VALUES (%s, %s)",
        (tid, subscription),
    )


def remove_subscription(cursor, tid, subscription):
    """A wrapper function for DELETE command of SQL.

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor.
        tid (int): Telegram ID of the user.
        subscription (str): Country name to unsubscribe.

    """
    cursor.execute(
        "DELETE FROM user WHERE tid = %s AND subscription = %s", (tid, subscription)
    )


def get_nonsubscribed_by_continent(cursor, tid, continent):
    """Returns countries of a continent which are not subscribed by a user

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor.
        tid (int): Telegram ID of the user.
        continent (str): The continent name.

    Returns:
        list(str): List of the country names, [] if empty.

    """
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
        return get(cursor, "name", "country")


def delete_user(cursor, tid):
    """Deletes the user and its data.

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor
        tid (int): Telegram ID of the user

    """
    cursor.execute("DELETE FROM user WHERE tid = %s", (tid))


def initialize_database():
    with connection() as cursor:
        create_tables(cursor)
        initialize_countries(cursor)


def create_tables(cursor):
    """Creates tables necessary for the bot.

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor

    """
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
    """Fetches country data (name, continent, cases, deaths, recovered, tests) from the API.

    Args:
        cursor (:obj:`mysql.connector.cursor.MySQLCursor`): Database cursor

    """
    countries = get(cursor, "name", "country")
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
