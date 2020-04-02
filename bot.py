# -*- coding: utf-8 -*-
import discord
from discord.ext import tasks, commands
from CoronaData.corona_virus_updater import update_data, get_corona_news
import datetime
from Gladiator.UserProfileData.backup_user_data import download_profiles

bot = commands.Bot(command_prefix="h!")

startup_extensions = ["gen", "gladiator", "meme", "trivia", "corona"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))

 # update corona virus data every x mins

@tasks.loop(hours=0.2)
async def corona_update_task():
    print("Updating coronavirus data")
    try:
        update_data()
        print("Updated coronavirus data")
        print("Trying to get the news")
        news = get_corona_news()
        channel = bot.get_channel(688045137162666051)
        if news:
            print("Updating news...")
            for k in news:
                await channel.send(k)
        else:
            print("There are no news")
    except Exception as e:
        print(f"Failed to complete the task and error occurred\n{e}")
        return
    
@bot.event
async def on_ready():
    print(f"Connected!\nName: {bot.user.name}\nId: {bot.user.id}\n")
    corona_update_task.start()
    await bot.change_presence(activity=discord.Game(name=f"with {len(bot.guilds)} server.Type h!help for commands"))
    download_profiles()
    
    
try:
    import bot_token
    bot.run(bot_token.token())
except ModuleNotFoundError:
    import os
    bot.run(os.environ['BOT_TOKEN'])
