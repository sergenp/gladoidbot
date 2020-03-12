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

            msg = f"Total Cases : **{country_data['TotalCases']}**\n"
            msg += f"New Cases : **{country_data['NewCases']}**\n"
            msg += f"Total Deaths : **{int(country_data['TotalDeaths']) if country_data['TotalDeaths'] is not None else 'None'}**\n"
            msg += f"New Deaths : **{int(country_data['NewDeaths']) if country_data['NewDeaths'] is not None else 'None'}**\n"
            msg += f"Total Recovered : **{int(country_data['TotalRecovered']) if country_data['TotalRecovered'] is not None else 'None'}**\n"
            msg += f"Active Cases : **{int(country_data['ActiveCases']) if country_data['ActiveCases'] is not None else 'None'}**\n"
            msg += f"Serious: **{int(country_data['Serious']) if country_data['Serious'] is not None else 'None'}**\n"
                
            await send_embed_message(ctx, title=country_data["Country"], content=msg)
        else:
            with open(os.path.join("CoronaData", "total_inf.json")) as f:
                corona = json.load(f)
            msg = f"Total Cases: **{corona['Total Cases']}**\nTotal Deaths: **{corona['Total Deaths']}**\nTotal Recovered: **{corona['Total Recovered']}**"
            await send_embed_message(ctx, title="Total Cases", content=msg)


def setup(bot):
    bot.add_cog(Corona(bot))
