# COVID-19 Worldwide Statistics Bot for Telegram

> *The Prophet (ﷺ) said, "If you hear of an outbreak of plague in a land, do not enter it; but if the plague breaks out in a place while you are in it, do not leave that place."*

*Sahih Al-Bukhari, Book 76 (Book of Medicine), Hadith 43*

<hr>

![Markdown Logo](./pic.png)

A Telegram Bot that sends you a notification when the statistics of a country you subscribed to gets updated.

Statistics are fetched from [disease.sh](https://github.com/disease-sh/API "NovelCovid/API Github page")

<hr>

## **What can this bot do?:**
* Sending notification when a subscribed country has new statistics.
* Getting statistics of a country with /get command

<hr>

## Installation:

### * Using docker:

Edit the below command with the necessary environmental variables and run:
```bash
docker run \
    -d --name cov19_tbot \
    --env CVBOT_API= \
    --env MYSQL_HOST= \
    --env MYSQL_DB= \
    --env MYSQL_USER= \
    --env MYSQL_PASSWORD= \
    meyagci/covid-19-telegram-bot
```

### * Normal installation:

Clone the repo to desired location:
```bash
git clone https://github.com/memreyagci/covid-19-telegram-bot
```

Install the requirements:
```bash
pip install -r requirements.txt
```

Set the following environmental variables:
```bash
export \
    CVBOT_API= \ #The API retrieved from BotFather
    MYSQL_HOST= \
    MYSQL_DB= \
    MYSQL_USER= \
    MYSQL_PASSWORD= \
```

Finally, run the bot.py file:
```bash
python bot.py
```
