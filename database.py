def create_tables(curr):
    curr.execute(
        """ CREATE TABLE IF NOT EXISTS users (
        telegram_id text
        subscribed_country text,
        language text
        ); """
        )

    curr.execute(
        """ CREATE TABLE IF NOT EXISTS statistics (
        country text UNIQUE,
        stats json
        ); """
        )

def get_users(curr):
    curr.execute("SELECT * FROM users")
    
    return list(curr.fetchall())

def get_user_subscriptons(curr, telegram_id):
    curr.execute("SELECT subscribed_country FROM users WHERE telegram_id = ?", (telegram_id,))

    return list(curr.fetchall())

def save_user():
    pass

def get_db_statistics(curr):
    curr.execute("SELECT stats FROM statistics")

    statistics = list(curr.fetchall())

    # statistics_dict = {
    #     "country" : statistics[0],
    #     "updated" : statistics[2],
    #     "cases" : statistics[3],
    #     "todayCases" : statistics[4],
    #     "deaths" : statistics[5],
    #     "todayDeaths" : statistics[6],
    #     "recovered" : statistics[7],
    #     "active" : statistics[8],
    #     "critical" : statistics[9],
    #     "casesPerOneMillion" : statistics[10],
    #     "deathsPerOneMillion" : statistics[11],
    #     "tests" : statistics[12],
    #     "testsPerOneMillion" : statistics[13],
    #     }

    return statistics

def update_statistics(curr, country, new_stats):
    curr.execute(
        """ UPDATE statistics 
            SET stats = ?
            WHERE country = ?
        """, (new_stats, country))





