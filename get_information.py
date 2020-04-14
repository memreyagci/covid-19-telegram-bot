import requests
import datetime
from database import get_db_statistics

# returns the countries in the api as a sorted list
def get_country_list():
    country_list = []

    for i in requests.get("https://corona.lmao.ninja/countries").json():
        country_list.append(i["country"])

    country_list.sort()

    return country_list

def check_if_updated(curr, db_last_statistics):
    country_list = []
    
    for i in db_last_statistics:
        country_json = requests.get("https://corona.lmao.ninja/countries/{}".format(i["country"])).json()

        if i["updated"] != country_json["updated"]:
            message_list =[]
            message_list.append(generate_update_message(country_json))
            country_list.append(i["country"])
            update_statistics(i["country"], country_json)
    
            return message_list, country_list

        else:
            return None

def generate_update_message(country_json):
    country_json["updated"] = datetime.datetime.fromtimestamp(country_json["updated"]//1000.0)
    message1 = "New update for \033[1m {} \033[0m {} in {} {}, {} {}:{}\n\n".format(
        country_json["country"],
        get_country_flag(country_json["countryInfo"]["iso2"]),
        updated.strftime("%B"),
        updated.strftime("%d"),
        updated.strftime("%Y"),
        updated.strftime("%H"),
        updated.strftime("%M")
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
            country_json["cases"],
            country_json["todayCases"],
            country_json["casesPerOneMillion"],
            country_json["deaths"],
            country_json["todayDeaths"],
            country_json["deathsPerOneMillion"],
            country_json["tests"],
            country_json["testsPerOneMillion"],
            country_json["recovered"],
            country_json["active"],
            country_json["tests"],
            country_json["critical"]
        )

    return message1 + message2

def get_country_flag(code):
    OFFSET = 127462 - ord('A')

    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)


        


    

