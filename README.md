# COVID-19 Worldwide Statistics Bot for Telegram

> *The Prophet (ﷺ) said, "If you hear of an outbreak of plague in a land, do not enter it; but if the plague breaks out in a place while you are in it, do not leave that place."*

*Sahih Al-Bukhari, Book 76 (Book of Medicine), Hadith 43*

<hr>

![Markdown Logo](./pic.png)

A Telegram Bot that sends you a notification when the statistics of a country you subscribed to gets updated.

Statistics are fetched from [disease.sh](https://github.com/disease-sh/API "NovelCovid/API Github page")

<hr>

### **What can this bot do?:**
* Sending notification when a subscribed country has new statistics.
* Getting statistics of a country with /get command

<hr>

To try it out, [create yourself a bot with BotFather](https://core.telegram.org/bots#6-botfather)

Then, while in desired direction:

```bash
git clone https://github.com/memreyagci/covid-19-telegram-bot
```

Install the requirements:

```
pip install -r requirements.txt
```

Create a file named 'database_config.py' in root directory of the repository and provide the necessary inputs:
```python
mysql = {
    "host": #host,
    "user": #user,
    "passwd": #passwd,
    "db": #db,
}
```

Set your bot's api as an environmental variable:

```bash
export CVBOT_API=
```

Finally, run the bot.py file:

```bash
python bot.py
```
