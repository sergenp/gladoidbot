import requests
from util import send_embed_message
from discord.ext import commands
import discord


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

    @commands.command()
    async def yesno(self, ctx, *args):
        data = requests.get("https://yesno.wtf/api/").json()
        await send_embed_message(ctx=ctx, image_url=data["image"])
    
    @commands.command()
    async def blb(self, ctx, user : discord.Member = None, gender='M'):
        if user:
            name = user.display_name
        else:
            name = ctx.message.author.display_name
        
        name = name.replace(" ", "%20")
        sex = gender.lower()
        await send_embed_message(ctx=ctx, image_url=f"https://belikebill.ga/billgen-API.php?default=1&name={name}&sex={sex}")

    @commands.command()
    async def swq(self, ctx):
        data = requests.get("http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote").json()
        await send_embed_message(ctx=ctx, content=data['starWarsQuote'])


def setup(bot):
    bot.add_cog(Meme(bot))
