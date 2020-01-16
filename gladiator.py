import discord
from discord.ext import commands


class Gladiator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def challenge(self, ctx, userToChallenge: discord.Member = None):
        if userToChallenge:
            await ctx.send(f"{ctx.message.author.mention} has challenged you {userToChallenge.mention} to a gladiator match")
        else:
            await ctx.send(f"{ctx.message.author.mention} you need to @ the people you wanna challenge")


def setup(bot):
    bot.add_cog(Gladiator(bot))
