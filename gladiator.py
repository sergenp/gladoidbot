import discord
from discord.ext import commands
import asyncio
from GladiatorGame import GladiatorGame
from util import send_embed_message
from discord import Member
from enum import Enum
import json
from discord import Emoji
import os


class Gladiator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # dictionary holding the id of the channel and the Game instance of the channel
        self.games = {}
        self.game_started = False
        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            self.attack_types = json.load(f)

        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            self.game_information = json.load(f)["game_information_texts"]

    @commands.command()
    async def gamead(self, ctx):
        await ctx.send(self.game_information["game_ad_text"])

    @commands.command()
    async def gamerules(self, ctx):
        channel = await ctx.message.author.create_dm()
        await send_embed_message(channel, GladiatorGame.construct_information_message())

    @commands.command()
    async def challenge(self, ctx, userToChallenge: discord.Member = None):
        if ctx.channel.id in self.games:
            await ctx.send(self.game_information["game_is_already_commencing_text"])
            return

        if userToChallenge:
            if userToChallenge.bot:
                await ctx.send(self.game_information["game_challenge_bot_text"].format(ctx.message.author.mention))
            else:
                msg = await ctx.send(self.game_information["game_challenge_text"].format(
                    ctx.message.author.mention, userToChallenge.mention, '👍', '👎'), delete_after=60.0)
                await msg.add_reaction('👍')
                await msg.add_reaction('👎')

                def check(reaction, user):
                    return user == userToChallenge and reaction.message.id == msg.id

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    if reaction.emoji == '👍':
                        self.game_started = True
                        self.games.update({ctx.channel.id: GladiatorGame(
                            ctx.message.author, userToChallenge)})

                        await msg.delete()
                        await send_embed_message(ctx, self.game_information["game_began_text"])
                        await self.gladiator_game_loop(ctx)

                    else:
                        await msg.delete()
                        await ctx.send(self.game_information["game_challenge_declined_text"].format(user.mention), delete_after=10)

                except asyncio.TimeoutError:
                    await msg.delete()
                else:
                    pass

        else:
            await ctx.send(self.game_information["game_challenge_user_mention_missing"].format(ctx.message.author.mention))

    async def gladiator_game_loop(self, ctx):
        game = self.games[ctx.channel.id]
        if game.next_turn():
            rand_ev = game.random_event()
            if rand_ev:
                await send_embed_message(ctx, rand_ev)

            attack_msg_text = self.game_information["game_turn_text"].format(
                game.current_player)

            for i in game.current_player.permitted_attacks:
                attack_msg_text += f"{i['name']} : {i['reaction_emoji']}\n"

            attack_msg = await send_embed_message(ctx, attack_msg_text)

            for i in game.current_player.permitted_attacks:
                await attack_msg.add_reaction(i["reaction_emoji"])

            def check(reaction, user):
                return user == game.current_player.Member and reaction.message.id == attack_msg.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                for i in game.current_player.permitted_attacks:
                    if i["reaction_emoji"] == reaction.emoji:
                        await send_embed_message(ctx, game.attack(i["id"], i["damage_type_id"]))
                        break
                else:
                    await send_embed_message(ctx, game.attack())

                await attack_msg.delete()
                await self.gladiator_game_loop(ctx)

            except asyncio.TimeoutError:
                await ctx.send(self.game_information["game_end_via_timeout_text"].format(game.players[1]))
                del self.games[ctx.channel.id]
        else:
            await ctx.send(self.game_information["game_over_text"].format(game.current_player, game.current_player))
            del self.games[ctx.channel.id]


def setup(bot):
    bot.add_cog(Gladiator(bot))
