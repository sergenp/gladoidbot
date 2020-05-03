# -*- coding: utf-8 -*-
import json
import os
import discord
import ast
from discord.ext import tasks, commands
from CoronaData.corona_virus_updater import update_data, get_corona_news
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

bot = commands.Bot(command_prefix=get_prefix)
startup_extensions = ["gen", "gladiator", "meme", "trivia", "corona"]
for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))


@tasks.loop(hours=0.2)
async def corona_update_task():
    news_channels = {}

    with open("guild_settings.json", "r") as f:
        news_channels = json.load(f)["corona_news_channel"]

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
                    if channel:
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
    await bot.change_presence(activity=discord.Game(name="www.hutbot.works"))
    corona_update_task.start()

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

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@bot.command(name="eval")
async def eval_fn(ctx, *, cmd):
    if ctx.author.id == 314800228480057355:
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        insert_returns(body)
        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        result = (await eval(f"{fn_name}()", env))
    else:
        await ctx.send("You aren't my creator, therefore I won't do your bidding.")

try:
    import bot_token
    bot.run(bot_token.token())
except (ModuleNotFoundError, ImportError):
    bot.run(os.environ['BOT_TOKEN'])
