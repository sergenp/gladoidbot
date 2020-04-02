# -*- coding: utf-8 -*-
import discord
from discord.ext import tasks, commands
from CoronaData.corona_virus_updater import update_data, get_corona_news
import datetime
from Gladiator.UserProfileData.backup_user_data import download_profiles
import json
import os


bot = commands.Bot(command_prefix="h!")

startup_extensions = ["gen", "gladiator", "meme", "trivia", "corona"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))


news_channels = {}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CoronaData", "guild_channel_data.json")) as f:
    news_channels = json.load(f)

 # update corona virus data every x mins
@tasks.loop(hours=0.2)
async def corona_update_task():
    global news_channels
    print("Updating coronavirus data")
    try:
        update_data()
        print("Updated coronavirus data")
        print("Trying to get the news")
        news = get_corona_news()
        if news:
            print("Updating news...")
            for guild in bot.guilds:
                try:
                    channel_id = news_channels[str(guild.id)]
                    for k in news:
                        await bot.get_channel(channel_id).send(k)
                except KeyError:
                    pass
        else:
            print("There are no news")
    except Exception as e:
        print(f"Failed to complete the task and error occurred\n{e}")
        return

@bot.event
async def on_ready():
    print(f"Connected!\nName: {bot.user.name}\nId: {bot.user.id}\n")
    await bot.change_presence(activity=discord.Game(name=f"with {len(bot.guilds)} servers. h!help for commands"))
    download_profiles()
    corona_update_task.start()
    

try:
    import bot_token
    bot.run(bot_token.token())
except ModuleNotFoundError:
    import os
    bot.run(os.environ['BOT_TOKEN'])
