import discord
from discord.ext import commands
import requests
from util import send_embed_message
import dateutil.parser

class Corona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_corona_virus_data = {}
    
    @commands.command(pass_context=True, description="Given country, it shows the specific cases inside that country, otherwise it shows general information about the virus")
    async def virus(self, ctx, country: str = None):
        async with ctx.typing():
            if country:
                data = requests.get(
                    "https://coronavirus-tracker-api.herokuapp.com/all").json()
                confirmed_msg = f""
                recovered_msg = f""
                died_msg = f""
                tot_confirmed = 0
                tot_recovered = 0
                tot_died = 0
                for dt in data['confirmed']['locations']:
                    if country.lower() in dt['country'].lower():
                        tot_confirmed += dt['latest']
                        if dt['province']:
                            confirmed_msg += f"{dt['province']} province has **{dt['latest']}** confirmed cases\n"

                for dt in data['recovered']['locations']:
                    if country.lower() in dt['country'].lower():
                        tot_recovered += dt['latest']
                        if dt['province']:
                            recovered_msg += f"{dt['province']} province has **{dt['latest']}** recovered cases\n"

                for dt in data['deaths']['locations']:
                    if country.lower() in dt['country'].lower():
                        tot_died += dt['latest']
                        if dt['province']:
                            died_msg += f"{dt['province']} province has **{dt['latest']}** death cases\n"

                msg = confirmed_msg + "Total confirmed cases : " + \
                    f"**{tot_confirmed}**\n"
                msg2 = died_msg + "Total deaths : " + \
                    f"**{tot_died}\n**"
                msg3 = recovered_msg + "Total recovered : " + \
                    f"**{tot_recovered}**"
                await send_embed_message(ctx, content=msg)
                await send_embed_message(ctx, content=msg2)
                await send_embed_message(ctx, content=msg3)
            else:
                data = self.parse_corona_information(requests.get(
                    "https://coronavirus-tracker-api.herokuapp.com/all").json())
                await send_embed_message(ctx, title="Current information about the coronavirus", content=f"There are a total of **{data['latest_confirmed']}** cases.\nOut of all those cases **{data['latest_recovered']}** people recovered and **{data['latest_died']}** people died.\nThese informations are last updated at {data['last_updated']}")
                if self.last_corona_virus_data:
                    old_data = self.parse_corona_information(
                        self.last_corona_virus_data)
                    await send_embed_message(ctx, title="What has changed since last call of this command", content=f"There is **{old_data['latest_confirmed'] - data['latest_confirmed']}** more confirmed cases.**{old_data['latest_recovered'] - data['latest_recovered']}** people has recovered.**{old_data['latest_died'] - data['latest_died']}** died.")

                self.last_corona_virus_data = data

    def parse_corona_information(self, data):
        latest_confirmed = data['latest']['confirmed']
        latest_died = data['latest']['deaths']
        latest_recovered = data['latest']['recovered']
        last_died_date = dateutil.parser.parse(
            data['deaths']['last_updated']).strftime("%b %d %Y %H:%M:%S")

        return {"latest_confirmed": latest_confirmed, "latest_died": latest_died, "latest_recovered": latest_recovered, "last_updated": last_died_date}


def setup(bot):
    bot.add_cog(Corona(bot))