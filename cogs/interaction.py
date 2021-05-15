import discord
from discord.ext import commands, tasks
from .util import send_embed_message
import os
import random
import aiohttp

TENOR_API_KEY = os.environ["TENOR_API_KEY"]


async def save_tenor_gifs(search):
    url = f"https://api.tenor.com/v1/search?q={search}&contentfilter=medium&media_filter=minimal&limit=20&key={TENOR_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                result = await r.json()
                urls = []
                for res in result["results"]:
                    urls.append(res["media"][0]["tinygif"]["url"])
                return urls


class Interaction(commands.Cog):
    def __init__(self, bot):
        """Hug, stab, do stuff to other members"""
        self.bot = bot
        self.update_gifs_task.start()
        self.gif_data = {}

    @tasks.loop(hours=4)
    async def update_gifs_task(self):
        gifs = ["hugs", "stabs", "pukes", "pats"]
        for gif in gifs:
            self.gif_data[gif] = await save_tenor_gifs(gif)

    async def create_gif(self, ctx, gif, user: discord.Member, **kwargs):
        gif_url = random.choice(self.gif_data[gif])
        if user is not None:
            title = f"{ctx.message.author.name} {gif} {kwargs.get('adjective', '')} {user.name}"
        else:
            title = f"{ctx.message.author.name} {gif} {kwargs.get('adjective', '')} {ctx.message.author.name}"

        await send_embed_message(ctx, image_url=gif_url, title=title)

    @commands.command()
    async def hug(self, ctx, mention: discord.Member = None):
        await self.create_gif(ctx, "hugs", mention)

    @commands.command()
    async def stab(self, ctx, mention: discord.Member = None):
        await self.create_gif(ctx, "stabs", mention)

    @commands.command()
    async def puke(self, ctx, mention: discord.Member = None):
        await self.create_gif(ctx, "pukes", mention, adjective="at")

    @commands.command()
    async def pat(self, ctx, mention: discord.Member = None):
        await self.create_gif(ctx, "pats", mention)


def setup(bot):
    bot.add_cog(Interaction(bot))
