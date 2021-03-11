from json import JSONDecodeError
from time import sleep

import pycountry_convert
import requests

OFFSET = 127462 - ord("A")


def fetch_data(country=None):
    """Fetches data of a country from the API.

    Args:
        country (str, optional): Name of country. All countries are fetched if empty.

    Returns:
        A dict of JSON file fetched from coron.lmao.ninja/v2/countries/{country}. For example:

        {'updated': 1615492408406,
         'country': 'Turkey',
         'countryInfo': {'_id': 792,
                         'iso2': 'TR',
                         'iso3': 'TUR',
                         'lat': 39,
                         'long': 35,
                         'flag': 'https://disease.sh/assets/img/flags/tr.png'},
         'cases': 2835989,
         'todayCases': 14046,
         'deaths': 29290,
         'todayDeaths': 63,
         'recovered': 2659093,
         'todayRecovered': 9231,
         'active': 147606,
         'critical': 1310,
         'casesPerOneMillion': 33379,
         'deathsPerOneMillion': 345,
         'tests': 34694624,
         'testsPerOneMillion': 408347,
         'population': 84963623,
         'continent': 'Asia',
         'oneCasePerPeople': 30,
         'oneDeathPerPeople': 2901,
         'oneTestPerPeople': 2,
         'activePerOneMillion': 1737.28,
         'recoveredPerOneMillion': 31296.84,
         'criticalPerOneMillion': 15.42}

    Raises:
        JSONDecodeError: When the website doesn't response because of too much request.
    """

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
    """Compares old data (on the database) with new (fetched from the API) to determine if there is a change.

    Args:
        country (str): Name of country.
        old_cases (int): Number of cases on database.
        old_deaths (int): Number of deaths on database.
        old_recovered (int): Number of recovered on database.
        old_tests (int): Number of tests on database.

    Returns:
        A dict mapping data name to a list of new number, difference, and that day's amount. For example:

        {'cases': [2835989, 35989, 9231],
         'deaths': [29290, 290, 63],
         'recovered': [2659093, 93, 9231],
         'tests': [34694624, 624]}
    """

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
    """Generates update message to be send to users.

    Args:
        country (str): Name of country.
        updates (dict): Updated data with new values.

    Returns:
        str: Message to be sent.
    """

    message = f"New update for {country}  {get_country_flag(country)}\n"

    if updates["cases"] != []:
        message += f"""
            Cases: {updates["cases"][0]:,} ({'+' if updates["cases"][1] > 0 else ''}{updates["cases"][1]:,})
            Today: {updates["cases"][2]:,}
            """
    if updates["deaths"] != []:
        message += f"""
            Deaths: {updates["deaths"][0]:,} ({'+' if updates["deaths"][1] > 0 else ''}{updates["deaths"][1]:,})
            Today: {updates["deaths"][2]:,}
            """
    if updates["recovered"] != []:
        message += f"""
            Recovered: {updates["recovered"][0]:,} ({'+' if updates["recovered"][1] > 0 else ''}{updates["recovered"][1]:,})
            Today: {updates["recovered"][2]:,}
            """
    if updates["tests"] != []:
        message += f"""
            Tests: {updates["tests"][0]:,} ({'+' if updates["tests"][1] > 0 else ''}{updates["tests"][1]:,})
            """

    return message


def get_new(country):
    """Fetches new data from the API.

    Args:
        country: Name of country.

    Returns:
        A tuple of total and today's cases, deaths, recovered, and tests (only total). For example:

        (2835989, 9231, 29290, 63, 2659093, 9231, 34694624)
    """

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
    """Fetches current wanted data of a country.

    Args:
        country (str): Name of country.
        data (str): Data to be fetched. Can be 'cases', 'deaths', 'recovered', or 'tests'.

    Returns:
        int: The amount of "data"
    """

    req = fetch_data(country)

    return req[data]


def get_country_alpha2(country):
    """Converts country name to its Alpha2 code.

    Args:
        country (str): Name of country

    Returns:
        str: Alpha2 code

    Raises:
        KeyError: If a country does not exist in pycountry_convert module.
    """

    try:
        code = pycountry_convert.country_name_to_country_alpha2(country)
    except KeyError:
        code = requests.get(f"https://corona.lmao.ninja/v2/countries/{country}").json()[
            "countryInfo"
        ]["iso2"]

    return code


def get_country_flag(country):
    """Generates flag emoji.

    Args:
        country (str): Name of country.

    Returns:
       str: Unicode of flag emoji.

    """

    code = get_country_alpha2(country)

    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)
