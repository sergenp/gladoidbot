# -*- coding: utf-8 -*-  
from discord.ext import commands
from CoronaData.corona_virus_updater import update_data 
import asyncio

try:
    import bot_token
except ModuleNotFoundError:
    import os

bot = commands.Bot(command_prefix="h!")

startup_extensions = ["gen", "gladiator", "meme", "trivia", "corona"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))

async def corona_update_task():
    while True:
        print("Updating coronavirus data")
        update_data()
        print("Updated coronavirus data")
        await asyncio.sleep(60*60*2) # update corona virus data every 2 hours

@bot.event
async def on_ready():
    print(f"Connected!\nName: {bot.user.name}\nId: {bot.user.id}\n")
    bot.loop.create_task(corona_update_task())

try:
    bot.run(bot_token.token())
except NameError:
    bot.run(os.environ['BOT_TOKEN'])
