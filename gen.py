import discord
from discord.ext import commands
from util import send_embed_message
from googletrans import Translator
import requests

TRANSLATOR = Translator()


def setup(bot):
    bot.add_cog(General(bot))


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Translates given text to english ")
    async def translate(self, ctx, *args):
        toTranslate = ""
        for arg in args:
            if isinstance(arg, str):
                toTranslate += arg + " "

        if toTranslate == "":
            await send_embed_message(ctx, "Gimme something to translate")
            return 
        
        detect_language = TRANSLATOR.detect(toTranslate).lang
        translated = TRANSLATOR.translate(toTranslate, src=detect_language, dest="en").text
        await send_embed_message(ctx, title=f"Language detected {detect_language.title()}", content=f"This:\n{toTranslate.title()}\nMeans:\n{translated.title()}")

    @commands.command()
    async def quote(self, ctx, amount=1):
        if amount > 10:
            amount = 10

        for _ in range(amount):
            data = requests.get("https://api.quotable.io/random").json()
            await send_embed_message(ctx, author_name=data["author"], content=data["content"])
    
    @commands.command(description="Returns the invite link of the bot")
    async def invite(self, ctx):
        await ctx.send("https://discordapp.com/api/oauth2/authorize?client_id=598077927577616384&permissions=117824&scope=bot")

    @commands.command(description="Shows the avatar of the user or the one mentioned")
    async def avatar(self, ctx, user:discord.Member = None):
        if user:
            await send_embed_message(ctx, title=f"Showing avatar of {user.name}", image_url=user.avatar_url)
        else:
            await send_embed_message(ctx, title=f"Showing avatar of {ctx.message.author.name}", image_url=ctx.message.author.avatar_url)