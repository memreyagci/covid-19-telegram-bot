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


def get_last_data(last_data) -> dict:
    """Generates a dict of data provided from the database.

    Args:
        last_data (tuple): Fetched data from the database, with SQL statement "SELECT * FROM country"

    Returns:
        A nested dict consisting of country name, its data, and their values. For instance:
            {"Turkey":
                {"cases": 2835989,
                 "deaths": 29290,
                 "recovered": 2659093,
                 "tests": 34694624}
                 }
    """

    dict_ = {}

    for i in last_data:
        dict_[i[0]] = {"cases": i[2], "deaths": i[3], "recovered": i[4], "tests": i[5]}

    return dict_


def check_updates(last_data, current_data) -> dict:
    """Compares old data (on the database) with new (fetched from the API) to determine if there is a change.

    Args:
        last_data (dict): Previously fetched of all countries, supposed to be provided via get_last_data
        current (dict): Newly fetched data from the API, supposed to be provided via get_current function.

    Returns:
        A nested dict of updated data mapping country name to its data and their amount of total, difference, and that day's. For example:

        {"Turkey":{"cases": {"total": 2835989,
                             "difference": 35989,
                             "today": 9231}
                             },
                   "recovered": {"total": 2659093,
                                 "difference": 93,
                                 "today": 9231}
                                 }
    """

    updates = {}

    for country in last_data.keys():
        for data in last_data[country].keys():
            if current_data[country][data] != last_data[country][data]:
                updates[country] = (
                    {} if country not in updates.keys() else updates[country]
                )

                if data != "tests":
                    updates[country][data] = {
                        "total": current_data[country][data],
                        "difference": current_data[country][data]
                        - last_data[country][data],
                        "today": current_data[country][f"today{str.title(data)}"],
                    }
                else:
                    updates[country][data] = {
                        "total": current_data[country][data],
                        "difference": current_data[country][data]
                        - last_data[country][data],
                    }

    return updates


def generate_update_message(updates) -> dict:
    """Generates update message to be send to users.

    Args:
        updates (dict): Updated data with new values.

    Returns:
        A dict of messages to be send mapping country names to their messages.
    """

    messages = {}

    for country in updates.keys():
        messages[country] = f"New update for {country}  {get_country_flag(country)}\n"

        for data in updates[country].keys():
            if data != "tests":
                messages[
                    country
                ] += f"""
            {str.title(data)}: {updates[country][data]["total"]:,} ({'+' if updates[country][data]["difference"] > 0 else ''}{updates[country][data]["difference"]:,})
            Today: {updates[country][data]["today"]:,}
                """
            else:
                messages[
                    country
                ] += f"""
            {str.title(data)}: {updates[country][data]["total"]:,} ({'+' if updates[country][data]["difference"] > 0 else ''}{updates[country][data]["difference"]:,})
                """

    return messages


def get_current() -> dict:
    """Fetches new data from the API.

    Returns:
        A nested dict mapping country names to their data and its values.
    """

    req = fetch_data()

    current_stats = {}

    for i in req:
        current_stats[i["country"]] = {
            "cases": i["cases"],
            "todayCases": i["todayCases"],
            "deaths": i["deaths"],
            "todayDeaths": i["todayDeaths"],
            "recovered": i["recovered"],
            "todayRecovered": i["todayRecovered"],
            "tests": i["tests"],
        }

    return current_stats


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
