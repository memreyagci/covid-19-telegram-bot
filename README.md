# COVID-19 Worldwide Statistics Bot for Telegram

> *The Prophet (ﷺ) said, "If you hear of an outbreak of plague in a land, do not enter it; but if the plague breaks out in a place while you are in it, do not leave that place."*<br>

*Sahih Al-Bukhari, Book 76 (Book of Medicine), Hadith 43*

<hr>

**The bot is still being developed, I don't have a published version that can be used yet. How to try it yourself with you own bot is shown below though. Feel free to contribute & suggest.**

A Telegram Bot that sends you a notification when the statistics of a country you subscribed to gets updated.

Statistics are fetched from [Novel COVID API](https://github.com/NovelCOVID/API "NovelCovid/API Github page")

<hr>

### **What works?:**
* Listing countries
* Saving user subscriptions
* Sending update messages

### **Issues:**
* Unsubscription doesn't work

<hr>

To try it out, [create yourself a bot with BotFather of Telegram](https://core.telegram.org/bots#6-botfather)

Then, while in the desired direction:

```bash
git clone https://github.com/memreyagci/covid-19-telegram-bot
```

Install the requirements:

```
pip install -r requirements.txt
```

Set your bot's api as an environmental variable:

```bash
export CVBOT_API=
```

Finally, run the bot.py file:

```bash
python bot.py
```