# -*- coding: utf-8 -*-
import json
import os
import discord
from discord.ext import tasks, commands
from CoronaData.corona_virus_updater import update_data, get_corona_news

try:
    import bot_token

    bot_token.configurate()
except (ModuleNotFoundError, ImportError):
    pass
from MongoDB.Connector import Connector


MongoDatabase = Connector()
MongoDatabase.download_gladiator_files_to_local()


def get_prefix(_, message):
    with open("guild_settings.json", "r") as f:
        prefixes = json.load(f)["prefixes"]

    return prefixes[str(message.guild.id)]


def prefix_load_and_save(func):
    def wrapper(*args, **kwargs):
        with open("guild_settings.json", "r") as f:
            prefixes = json.load(f)
        new_prefixes = func(*args, prefixes=prefixes["prefixes"], **kwargs)
        prefixes["prefixes"] = new_prefixes
        with open("guild_settings.json", "w") as t:
            json.dump(prefixes, t, indent=4)
        MongoDatabase.save_guild_settings(prefixes)

    return wrapper


@prefix_load_and_save
def get_default_prefix(guild_id: int, **kwargs):
    prefix = kwargs.get("prefixes")
    prefix[str(guild_id)] = "h!"
    return prefix


@prefix_load_and_save
def change_prefix_and_save(guild_id: int, new_prefix: str, **kwargs):
    prefix = kwargs.get("prefixes")
    prefix[str(guild_id)] = new_prefix
    return prefix


@prefix_load_and_save
def remove_guild_from_prefix(guild_id: int, **kwargs):
    prefix = kwargs.get("prefixes")
    prefix.pop(str(guild_id))
    return prefix


# load cogs
bot = commands.Bot(
    command_prefix=get_prefix,
    help_command=commands.MinimalHelpCommand(no_category="Rest"),
)
startup_extensions = [
    "gen",
    "gladiator",
    "meme",
    "trivia",
    "corona",
    "interaction",
    "big5_test",
]
for extension in startup_extensions:
    try:
        bot.load_extension("cogs." + extension)
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print("Failed to load extension {}\n{}".format(extension, exc))

# send corona related news to channels
@tasks.loop(hours=1)
async def corona_news_task():
    news_channels = {}
    with open("guild_settings.json", "r") as f:
        news_channels = json.load(f)["corona_news_channel"]
    news = get_corona_news()
    if news:
        print("Sending news...")
        for guild in bot.guilds:
            try:
                channel = bot.get_channel(news_channels[str(guild.id)])
                if channel:
                    for k in news:
                        await channel.send(k)
            except KeyError:
                pass
        print("Sent news")
    else:
        print("There are no news")


# get updated corona stats
@tasks.loop(hours=1)
async def corona_statistics_task():
    print("Updating coronavirus data")
    try:
        update_data()
        print("Updated coronavirus data")
    except Exception as e:
        print(f"Failed to complete the task and error occurred\n{e}")
        return


@bot.event
async def on_ready():
    print(f"Connected!\nName: {bot.user.name}\nId: {bot.user.id}\n")
    await bot.change_presence(activity=discord.Game(name="gladoid.herokuapp.com"))
    corona_statistics_task.start()
    corona_news_task.start()


@bot.event
async def on_guild_join(guild):
    get_default_prefix(guild.id)


@bot.event
async def on_guild_remove(guild):
    remove_guild_from_prefix(guild.id)


@bot.command(name="changeprefix")
async def change_prefix(ctx, prefix: str):
    if ctx.message.author.permissions_in(ctx.channel).manage_channels:
        change_prefix_and_save(ctx.guild.id, prefix)
        await ctx.send(f"Changed bot prefix to {prefix}")
    else:
        await ctx.send("You don't have permission to do this action.")


bot.run(os.environ["BOT_TOKEN"])
