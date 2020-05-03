import requests
import pycountry_convert
import json
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON, and_
from sqlalchemy.sql import select, insert, update, delete

class Database:
    def __init__(self):
        engine = create_engine('sqlite:///covid19.db?check_same_thread=False')
        self.create_tables(engine)
        self.conn = engine.connect()

    def get_connection(self):
        return self.conn

    def create_tables(self, engine):
        meta = MetaData()

        self.user = Table(
            'user', meta,
            Column('telegram_id', Integer),
            Column('subscribed_country', String),
        )
        self.country = Table(
            'country', meta,
            Column('country_name', String),
            Column('country_continent', String, unique=True),
            Column('country_stats', JSON),
        )
        meta.create_all(engine)

    def get_all_countries(self, conn):
        statement = select([self.country.c.country_name])
        all_countries = []

        for i in conn.execute(statement).fetchall():
            all_countries.append(i[0])

        return all_countries    

    def get_users(self, conn):
        statement = select([self.user])
        users_subscriptions = []

        for i in conn.execute(statement).fetchall():
            users_subscriptions.append(list(i))

        return users_subscriptions

    def get_user_ids(self, conn):
        statement = select([self.user.telegram_id.distinct()])
        users_ids = []

        for i in conn.execute(statement).fetchall():
            users_ids.append(i[0])

        return users_ids

    def get_user_subscriptions(self, conn, telegram_id):
        statement = select([self.user.c.subscribed_country]).where(self.user.c.telegram_id == telegram_id)
        subscription_list = []
        
        for i in conn.execute(statement).fetchall():
            subscription_list.append(list(i)[0])
        
        return subscription_list

    def get_country_by_continent(self, conn, country_continent):
        statement = select([self.country.country_name]).where(country.country_continent == country_continent)
        country_list = []

        for i in conn.execute(statement).fetchall():
            country_list.append(list(i)[0])

        return country_list

    def check_new_country(self, conn):
        countries = self.get_all_countries(conn)

        try:
            countries_api = requests.get("https://corona.lmao.ninja/v2/countries").json()
        except json.decoder.JSONDecodeError: #To prevent crashing of bot.py in case of Error 502 of corona.lmao.ninja
            pass
        else:
            for i in range(len(countries_api)):
                if countries_api[i]["country"] not in countries:
                    try:
                        continent = pycountry_convert.convert_continent_code_to_continent_name(pycountry_convert.country_alpha2_to_continent_code(countries_api[i]["countryInfo"]["iso2"]))
                        statement = self.country.insert().values(country_name=countries_api[i]["country"], country_continent=continent).prefix_with('OR IGNORE')
                        conn.execute(statement)
                    except:
                        pass

            return self.get_all_countries(conn)

    def check_if_updated(self, conn, country_name):
        statement = select([self.country.c.country_stats]).where(self.country.c.country_name == country_name)

        try:
            req = requests.get("https://corona.lmao.ninja/v2/countries/{}".format(country_name)).json()
        except:
            pass
        else:
            new_stats = [req["cases"] , req["deaths"], req["recovered"] , req["active"], req["critical"] , req["tests"]]

            try:
                last_stats = json.loads(conn.execute(statement).fetchone()[0])
            except:
                statement = self.country.update().where(self.country.c.country_name == country_name).values(country_stats = json.dumps(new_stats))
                conn.execute(statement)
            else:
                if last_stats != new_stats:
                    statement = self.country.update().where(self.country.c.country_name == country_name).values(country_stats = json.dumps(new_stats))
                    conn.execute(statement)
                    return True
                else:
                    return False

    def save_user_subscription(self, conn, telegram_id, subscribed_country):
        statement = self.user.insert().values(telegram_id=telegram_id, subscribed_country=subscribed_country)
        conn.execute(statement)

    def remove_user_subscription(self, conn, telegram_id, country_to_unsubscribe):
        statement = self.user.delete().where(and_(self.user.c.telegram_id == telegram_id, self.user.c.subscribed_country == country_to_unsubscribe))
        conn.execute(statement)

    def get_nonsubscribed_countries_by_continent(self, conn, telegram_id, country_continent):
        to_exclude = select([self.user.c.subscribed_country]).where(
                    self.user.c.telegram_id == telegram_id)
        # notin = []

        # for i in conn.execute(statement1).fetchall():
        #     notin.append(list(i)[0])
        # notin.append("Turkey")
        # print(notin)

        # statement2 = select([self.country.c.country_name]).where(
        #     and_(
        #         self.country.c.country_name.notin_(notin), 
        #         self.country.c.country_continent == country_continent
        #         )
        #             )

        statement2 = select([self.country.c.country_name]).where(
            and_(
                self.country.c.country_name.notin_(
                    to_exclude), 
                    self.country.c.country_continent == country_continent
                )
                    )

        nonsubscribed_countries = []

        for i in conn.execute(statement2).fetchall():
            nonsubscribed_countries.append(i[0])

        return nonsubscribed_countries

    def delete_user(self, conn, telegram_id):
        statement = user.delete().where(user.c.telegram_id == telegram_id)
        conn.execute(statement)