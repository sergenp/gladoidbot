import discord
from discord.ext import commands
import requests
from util import send_embed_message
import os
import json


class Corona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Given country, it shows the specific cases inside that country, otherwise it shows general information about the virus. Information about the virus is gotten from the https://www.worldometers.info/coronavirus/")
    async def virus(self, ctx, country: str = None):
        if country:
            corona = {}
            with open(os.path.join("CoronaData", "data.json")) as f:
                corona = json.load(f)

            country_data = {}
            for ctr in corona:
                if country.lower() == ctr["Country"].lower():
                    country_data = ctr
                    break
            else:
                await ctx.send(f"Couldn't find any info about country {country}")
                return
            msg = f""
            for keys in country_data:
                msg += f"{keys} : **{country_data.get(keys, 0)}**\n"
            await send_embed_message(ctx, title=country_data["Country"], content=msg)
        else:
            with open(os.path.join("CoronaData", "total_inf.json")) as f:
                corona = json.load(f)
            msg = f"Total Cases: **{corona['Total Cases']}**\nTotal Deaths: **{corona['Total Deaths']}**\nTotal Recovered: **{corona['Total Recovered']}**"
            await send_embed_message(ctx, title="Total Cases", content=msg)


def setup(bot):
    bot.add_cog(Corona(bot))
