import discord
from discord.ext import commands
import asyncio
from GladiatorGame import GladiatorGame
from GladiatorPlayer import AttackTypes
from util import send_embed_message
from discord import Member


class Gladiator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.game_started = False
        self.Game = None

    @commands.command()
    async def test(self, ctx):
        await ctx.send('<@314800228480057355>')

    @commands.command()
    async def challenge(self, ctx, userToChallenge: discord.Member = None):
        if self.game_started:
            await ctx.send("A game is already commencing")
            return

        if userToChallenge:
            if userToChallenge.bot:
                await ctx.send(f"{ctx.message.author.mention} has been killed by the power of AI. Dont mess with robots.")
            else:
                msg = await ctx.send(f"{ctx.message.author.mention} has challenged you {userToChallenge.mention} to a gladiator match\nTo accept react this message with 👍 to decline, 👎\nYou have 30 seconds to decide", delete_after=30)
                await msg.add_reaction('👍')
                await msg.add_reaction('👎')

                def check(reaction, user):
                    return user == userToChallenge and reaction.message.id == msg.id

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    if reaction.emoji == '👍':
                        self.game_started = True
                        if self.Game == None:
                            self.Game = GladiatorGame(
                                ctx.message.author, userToChallenge)

                        await msg.delete()
                        await send_embed_message(ctx, f"**THE GLADIATOR GAMES HAVE BEGUN**")
                        await self.gladiator_game_loop(ctx)

                    elif reaction.emoji == '👎':
                        await ctx.send(f"{user.mention} has declined the challenge. Pussy.")
                        await msg.delete()

                    return
                except asyncio.TimeoutError:
                    pass
                else:
                    pass

        else:
            await ctx.send(f"{ctx.message.author.mention} you need to @ the people you wanna challenge")

    async def gladiator_game_loop(self, ctx):
        if self.Game.next_turn():
            attack_msg = await send_embed_message(ctx, f"It is {self.Game.current_player.Member.mention}'s turn\n"
                                                  "What kind of attack do you want to do? \n"
                                                  "Thrust = :one:\n"
                                                  "Slash = :two:\n"
                                                  "Defensive = :three:\n"
                                                  "Flurry = :four:")

            await attack_msg.add_reaction('1️⃣')
            await attack_msg.add_reaction('2️⃣')
            await attack_msg.add_reaction('3️⃣')
            await attack_msg.add_reaction('4️⃣')

            def check(reaction, user):
                return user == self.Game.current_player.Member and reaction.message.id == attack_msg.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                if reaction.emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']:
                    if reaction.emoji == '1️⃣':
                        await send_embed_message(ctx, self.Game.attack(AttackTypes.Thrust))
                    elif reaction.emoji == '2️⃣':
                        await send_embed_message(ctx, self.Game.attack(AttackTypes.Slash))
                    elif reaction.emoji == '3️⃣':
                        await send_embed_message(ctx, self.Game.attack(AttackTypes.Defensive))
                    elif reaction.emoji == '4️⃣':
                        await send_embed_message(ctx, self.Game.attack(AttackTypes.Flurry))

                    rand_ev = self.Game.random_event()
                    if rand_ev:
                        await send_embed_message(ctx, rand_ev)
                    await attack_msg.delete()
                    await self.gladiator_game_loop(ctx)
            except asyncio.TimeoutError:
                await ctx.send(f"Game has ended via timeout, winner is {self.Game.players[1]}")
                self.Game = None
                self.game_started = False
        else:
            await ctx.send(f"{self.Game.current_player.Member.mention} is dead! Game is over. Get fucked {self.Game.current_player.Member.mention}")
            self.Game = None
            self.game_started = False


def setup(bot):
    bot.add_cog(Gladiator(bot))
