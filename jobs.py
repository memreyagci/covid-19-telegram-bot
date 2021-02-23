from json import JSONDecodeError
import requests
import pycountry_convert
from time import sleep

OFFSET = 127462 - ord("A")


def fetch_data(country=None):
    try:
        if country is not None:
            data = requests.get(
                f"https://corona.lmao.ninja/v2/countries/{get_country_alpha2(country)}"
            ).json()
        else:
            data = requests.get("https://corona.lmao.ninja/v2/countries").json()
    except JSONDecodeError:
        sleep(5)
        data = fetch_data(country)
    else:
        return data


def check_updates(country, old_cases, old_deaths, old_recovered, old_tests):
    (
        new_cases,
        today_cases,
        new_deaths,
        today_deaths,
        new_recovered,
        today_recovered,
        new_tests,
    ) = get_new(country)

    updates = {"cases": [], "deaths": [], "recovered": [], "tests": []}

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
    message = f"New update for {country}  {get_country_flag(country)}\n"

    if updates["cases"] != []:
        message += f"""
            Cases: {updates["cases"][0]} (+{updates["cases"][1]})
            Today: {updates["cases"][2]}
            """
    if updates["deaths"] != []:
        message += f"""
            Deaths: {updates["deaths"][0]} (+{updates["deaths"][1]})
            Today: {updates["deaths"][2]}
            """
    if updates["recovered"] != []:
        message += f"""
            Recovered: {updates["recovered"][0]} (+{updates["recovered"][1]})
            Today: {updates["recovered"][2]}
            """
    if updates["tests"] != []:
        message += f"""
            Tests: {updates["tests"][0]} (+{updates["tests"][1]})
            """

    return message


def get_new(country):
    req = fetch_data(country)

    new_cases = req["cases"]
    today_cases = req["todayRecovered"]
    new_deaths = req["deaths"]
    today_deaths = req["todayDeaths"]
    new_recovered = req["recovered"]
    today_recovered = req["todayRecovered"]
    new_tests = req["tests"]

    return (
        new_cases,
        today_cases,
        new_deaths,
        today_deaths,
        new_recovered,
        today_recovered,
        new_tests,
    )


def get_data(country, data):
    req = fetch_data(country)

    return req[data]


def get_country_alpha2(country):
    try:
        code = pycountry_convert.country_name_to_country_alpha2(country)
    except (KeyError, TypeError):
        code = requests.get(f"https://corona.lmao.ninja/v2/countries/{country}").json()[
            "countryInfo"
        ]["iso2"]

    return code


def get_country_flag(country):
    code = get_country_alpha2(country)

    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)
