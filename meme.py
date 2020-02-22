import requests
from util import send_embed_message
from discord.ext import commands


class Meme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        json_data = requests.get("https://meme-api.herokuapp.com/gimme").json()
        await send_embed_message(
            ctx=ctx, content=f"r/{json_data['subreddit']}\n{json_data['postLink']}", title=json_data['title'], image_url=json_data['url'])
    
    @commands.command(name="dadjoke")
    async def dad_joke(self, ctx):
        headers = {'Accept': 'text/plain'}
        await ctx.send(requests.get("https://icanhazdadjoke.com/", headers=headers).text)


def setup(bot):
    bot.add_cog(Meme(bot))
