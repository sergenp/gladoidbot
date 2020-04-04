# -*- coding: utf-8 -*-
import discord
from discord.ext import tasks, commands
from CoronaData.corona_virus_updater import update_data, get_corona_news
import datetime
from Gladiator.UserProfileData.backup_user_data import download_profiles, backup_single_profile
import json
import os


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


bot = commands.Bot(command_prefix=get_prefix)

startup_extensions = ["gen", "gladiator", "meme", "trivia", "corona"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))

 # update corona virus data every x mins

def prefix_load_and_save(func):
    def wrapper(*args, **kwargs):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        new_prefix = func(*args, prefixes=prefixes, **kwargs)
        with open("prefixes.json", "w") as t:
            json.dump(new_prefix, t, indent=4)
        backup_single_profile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefixes.json"))
    return wrapper

@prefix_load_and_save
def get_default_prefix(guild_id : int, **kwargs):
    prefix = kwargs.get("prefixes")
    prefix[str(guild_id)] = "h!"
    return prefix

@prefix_load_and_save
def change_prefix_and_save(guild_id : int, new_prefix : str, **kwargs):
    prefix = kwargs.get("prefixes")
    prefix[str(guild_id)] = new_prefix
    return prefix

@prefix_load_and_save
def remove_guild_from_prefix(guild_id : int, **kwargs):
    prefix = kwargs.get("prefixes")
    prefix.pop(str(guild_id))
    return prefix


@tasks.loop(hours=0.2)
async def corona_update_task():
    news_channels = {}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CoronaData", "guild_channel_data.json")) as f:
        news_channels = json.load(f)
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
                    channel = bot.get_channel(news_channels[str(guild.id)])
                    for k in news:
                        await channel.send(k)
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
    await bot.change_presence(activity=discord.Game(name=f"with {len(bot.guilds)} guilds. h!help for commands"))
    download_profiles()
    corona_update_task.start()

@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=discord.Game(name=f"with {len(bot.guilds)} guilds. h!help for commands"))
    get_default_prefix(guild.id)

@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(activity=discord.Game(name=f"with {len(bot.guilds)} guilds. h!help for commands"))
    remove_guild_from_prefix(guild.id)
    
@bot.command(name="changeprefix")
async def change_prefix(ctx, prefix : str):
    if ctx.message.author.permissions_in(ctx.channel).manage_channels:
        change_prefix_and_save(ctx.guild.id, prefix)
        await ctx.send(f"Changed bot prefix to {prefix}")
    else:
        await ctx.send(f"You don't have permission to do this action.")

try:
    import bot_token
    bot.run(bot_token.token())
except ModuleNotFoundError:
    import os
    bot.run(os.environ['BOT_TOKEN'])
