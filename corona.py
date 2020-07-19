from discord.ext import commands
from util import send_embed_message
import os
import json
from MongoDB.Connector import Connector

class Corona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Given country, it shows the specific cases inside that country, otherwise it shows general information about the virus.")
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

            def convert_to_int(value):
                try:
                    return "{:,}".format(int(country_data[value])) if country_data[value] is not None else 'None'
                except ValueError:
                    return country_data[value]

            msg = f"Total Cases : **{convert_to_int('TotalConfirmed')}**\n"
            msg += f"New Cases : **{country_data['NewConfirmed']}**\n"
            msg += f"Total Deaths : **{convert_to_int('TotalDeaths')}**\n"
            msg += f"New Deaths : **{convert_to_int('NewDeaths')}**\n"
            msg += f"Total Recovered : **{convert_to_int('TotalRecovered')}\n**"
            msg += f"New Recovered : **{convert_to_int('NewRecovered')}\n**"

            await send_embed_message(ctx, title=country_data["Country"], content=msg)
        else:
            with open(os.path.join("CoronaData", "total_inf.json")) as f:
                corona = json.load(f)
            msg = ""
            for k in corona:
                msg += f"{k} : **{corona[k]:,}**\n"
            await send_embed_message(ctx, title="Total Cases", content=msg)

    @commands.command(name="setnewschannel", pass_context=True, description="Sets the current channel as the corona news channel.\nBot will send news about corona virus to this channel after using this command")
    async def set_channel(self, ctx):
        if ctx.message.author.permissions_in(ctx.channel).manage_channels:
            MongoDatabase = Connector()
            news_channel_data_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "guild_settings.json")
            data = json.load(open(news_channel_data_path, "r"))
            data["corona_news_channel"][str(ctx.guild.id)] = ctx.channel.id
            with open(news_channel_data_path, "w") as f:
                json.dump(data, f)
            MongoDatabase.save_guild_settings(data)
            await ctx.send("Succesfully set this channel to be the corona news channel")
        else:
            await ctx.send("You don't have required permissions to do this action.")

def setup(bot):
    bot.add_cog(Corona(bot))
