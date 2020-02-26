import discord
from discord.ext import commands
from util import send_embed_message, search_youtube
from googletrans import Translator
import requests
from cowpy import cow

TRANSLATOR = Translator()


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ysearch")
    async def youtubeSearch(self, ctx, *searchStr):
        searchStr = ' '.join(map(str, searchStr))
        await ctx.send(f"Searching  \'{searchStr}\' on youtube...")
        video_link = search_youtube(searchStr)
        if video_link != None:
            await ctx.send(f"Found : {video_link}")
        else:
            await ctx.send("I couldn't find anything")

    @commands.command(pass_context=True, description="Example usage:\n h!translate \'I love you\' german")
    async def translate(self, ctx, toTranslate: str = "", toTranslateLanguage: str = "en"):
        if toTranslate == "":
            await send_embed_message(ctx, "Gimme something to translate")
        try:
            detect_language = TRANSLATOR.detect(toTranslate).lang
            print(f"Language detected from {toTranslate}, {detect_language}")
            translated = TRANSLATOR.translate(
                toTranslate, src=detect_language, dest=toTranslateLanguage).text
            await send_embed_message(ctx, f"This:\n{toTranslate.upper()}\nMeans:\n{translated.upper()}")
        except ValueError:
            await send_embed_message(ctx, "Error, type h!help translate")
    
    @commands.command()
    async def quote(self, ctx, amount=1):
        if amount>10:
            amount = 10
            
        for i in range(amount):
            data = requests.get("https://api.quotable.io/random").json()
            await send_embed_message(ctx, author_name=data["author"], content=data["content"])

def setup(bot):
    bot.add_cog(General(bot))
