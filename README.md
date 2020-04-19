# COVID-19 Worldwide Statistics Bot for Telegram

> *The Prophet (ﷺ) said, "If you hear of an outbreak of plague in a land, do not enter it; but if the plague breaks out in a place while you are in it, do not leave that place."*

*Sahih Al-Bukhari, Book 76 (Book of Medicine), Hadith 43*

<hr>

![Markdown Logo](/botpic.png)

**Here is the bot: [@COVID19WorldwideStatisticsBot](https://t.me/COVID19WorldwideStatisticsBot)**

A Telegram Bot that sends you a notification when the statistics of a country you subscribed to gets updated.

Statistics are fetched from [Novel COVID API](https://github.com/NovelCOVID/API "NovelCovid/API Github page")

<hr>

### **What works?:**
* Listing countries
* Saving user subscriptions
* Sending update messages

### **Issues:**
* ~~Unsubscription doesn't work~~ I found a workaround, although it might not be the best way to solve. See [this commit](https://github.com/memreyagci/covid-19-telegram-bot/commit/db96e57037b958c3c827e329679a09bc9711f032 "commit db96e57037b958c3c827e329679a09bc9711f032").

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