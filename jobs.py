import requests
import pycountry_convert

OFFSET = 127462 - ord('A')

def check_updates(country, old_cases, old_deaths, old_recovered, old_tests):
    new_cases, today_cases, new_deaths, today_deaths, new_recovered, today_recovered, new_tests = get_new(country)

    updates = {
            "cases": [],
            "deaths": [],
            "recovered": [],
            "tests": []
            }

    changed = 1

    if new_cases != old_cases:
        updates["cases"].append(new_cases)
        updates["cases"].append(new_cases - old_cases)
        updates["cases"].append(today_cases)
        changed = 0
    if new_deaths != old_deaths:
        updates["deaths"].append(new_deaths)
        updates["deaths"].append(new_deaths - old_deaths)
        updates["deaths"].append(today_deaths)
        changed = 0
    if new_recovered != old_recovered:
        updates["recovered"].append(new_recovered)
        updates["recovered"].append(new_recovered - old_recovered)
        updates["recovered"].append(today_recovered)
        changed = 0
    if new_tests != old_tests:
        updates["tests"].append(new_tests)
        updates["tests"].append(new_tests - old_tests)
        changed = 0

    if changed == 1:
        return False

    return updates

def generate_update_message(country, updates):
    message = "New update for {}  {}\n".format(
                                    country,
                                    get_country_flag(country)
                                                )
    if updates["cases"] != []:
        message += """
            Cases: {} (+{})
            Today: {}
            """.format(
                    updates["cases"][0],
                    updates["cases"][1],
                    updates["cases"][2]
                    )
    if updates["deaths"] != []:
        message += """
            Deaths: {} (+{})
            Today: {}
            """.format(
                    updates["deaths"][0],
                    updates["deaths"][1],
                    updates["deaths"][2]
                    )
    if updates["recovered"] != []:
        message += """
            Recovered: {} (+{})
            Today: {}
            """.format(
                    updates["recovered"][0],
                    updates["recovered"][1],
                    updates["recovered"][2]
                    )
    if updates["tests"] != []:
        message += """
            Tests: {} (+{})
            """.format(
                    updates["tests"][0],
                    updates["tests"][1]
                    )
    return message

def get_new(country):
    req = requests.get("https://corona.lmao.ninja/v2/countries/{}".format(country)).json()

    new_cases = req["cases"]
    today_cases = req["todayRecovered"]
    new_deaths = req["deaths"]
    today_deaths = req["todayDeaths"]
    new_recovered = req["recovered"]
    today_recovered = req["todayRecovered"]
    new_tests = req["tests"]

    return new_cases, today_cases, new_deaths, today_deaths, new_recovered, today_recovered, new_tests

def get_country_flag(country):
    try:
        code = pycountry_convert.country_name_to_country_alpha2(country)
    except:
        code = requests.get("https://corona.lmao.ninja/v2/countries/{}"
                            .format(country)).json()["countryInfo"]["iso2"]

    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)
