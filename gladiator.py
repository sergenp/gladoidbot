import discord
from discord.ext import commands
import asyncio


class Gladiator(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    async def challenge(self, ctx, userToChallenge: discord.Member = None):
        if userToChallenge:
            if userToChallenge.bot:
                await ctx.send(f"{ctx.message.author.mention} has been killed by the power of AI. Dont mess with robots.")
                return
            else:
                msg = await ctx.send(f"{ctx.message.author.mention} has challenged you {userToChallenge.mention} to a gladiator match\nTo accept react this message with 👍 to decline, 👎\nYou have 30 seconds to decide", delete_after=30)

                def check(reaction, user):
                    return user == userToChallenge and reaction.message.id == msg.id

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    if reaction.emoji == '👍':
                        await ctx.send(f"{user.mention} accepted the challenge.")
                    elif reaction.emoji == '👎':
                        await ctx.send(f"{user.mention} has declined the challenge. Pussy.")

                except asyncio.TimeoutError:
                    pass
                else:
                    pass

        else:
            await ctx.send(f"{ctx.message.author.mention} you need to @ the people you wanna challenge")


def setup(bot):
    bot.add_cog(Gladiator(bot))
