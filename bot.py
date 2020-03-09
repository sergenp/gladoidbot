# -*- coding: utf-8 -*-  
from discord.ext import commands
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

@bot.event
async def on_ready():
    print(f"Connected!\nName: {bot.user.name}\nId: {bot.user.id}\n")

try:
    bot.run(bot_token.token())
except NameError:
    bot.run(os.environ['BOT_TOKEN'])
