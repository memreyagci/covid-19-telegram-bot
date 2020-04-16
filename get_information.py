import requests
import datetime
import pycountry_convert

def generate_update_message(country_name):
    new_stats = requests.get("https://corona.lmao.ninja/countries/{}".format(country_name)).json()
    #update_time = datetime.datetime.fromtimestamp(new_stats["updated"]//1000.0)

    #message1 = "New update for {}  {} in {} {}, {} {}:{}\n".format(
    message1 = "New update for {}  {}\n".format(
        new_stats["country"],
        get_country_flag(country_name),
        # get_country_flag(country_name),
        # update_time.strftime("%B"),
        # update_time.strftime("%d"),
        # update_time.strftime("%Y"),
        # update_time.strftime("%H"),
        # update_time.strftime("%M")
            )

    message2 = """ 
        Total cases: {}
        Today: {}
        Cases per one million: {}

        Deaths: {}
        Today: {}
        Deaths per one million: {}

        Tests: {}
        Tests per one million: {}

        Recovered: {}
        Active cases: {}
        Critical: {}
        """.format(
            new_stats["cases"],
            new_stats["todayCases"],
            new_stats["casesPerOneMillion"],
            new_stats["deaths"],
            new_stats["todayDeaths"],
            new_stats["deathsPerOneMillion"],
            new_stats["tests"],
            new_stats["testsPerOneMillion"],
            new_stats["recovered"],
            new_stats["active"],
            new_stats["tests"],
            new_stats["critical"]
        )

    print(message1+message2)

    return message1 + message2

def get_country_flag(country_name):
    code = requests.get("https://corona.lmao.ninja/countries/{}".format(country_name)).json()["countryInfo"]["iso2"]

    OFFSET = 127462 - ord('A')

    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)