import discord
from discord.ext import commands
import asyncio
from Gladiator.GladiatorGame import GladiatorGame, GladiatorStats
from Gladiator.GladiatorProfile import GladiatorProfile
from util import send_embed_message
from enum import Enum
import json
import os

class Gladiator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # dictionary holding the id of the channel and the Game instance of the channel
        self.games = {}
        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            self.attack_types = json.load(f)

        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            self.game_information = json.load(f)["game_information_texts"]

        with open(os.path.join("Gladiator", "Equipments", "GladiatorEquipments.json")) as f:
            self.equipments = json.load(f)

        with open(os.path.join("Gladiator", "Equipments", "GladiatorSlots.json")) as f:
            self.equipment_slots = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorTurnDebuffs.json")) as f:
            self.debuffs = json.load(f)

    @commands.command()
    async def gamead(self, ctx):
        await ctx.send(self.game_information["game_ad_text"])

    @commands.command()
    async def gamerules(self, ctx):
        channel = await ctx.message.author.create_dm()
        await send_embed_message(channel, GladiatorGame.construct_information_message())

    @commands.command()
    async def profile(self, ctx, userProfileToDisplay: discord.Member = None):
        profile = None
        if userProfileToDisplay:
            profile = GladiatorProfile(userProfileToDisplay)
        else:
            profile = GladiatorProfile(ctx.message.author)

        msg = ""
        for key in profile.profile_stats.keys():
            if not key in ("Id", "armor_id", "weapon_id", "boosts"):
                if key == "Inventory":
                    for item in profile.profile_stats[key]:
                        msg += f"{item['type']} : **{item['name']}\n**"
                    continue
                msg += f"{key} : **{profile.profile_stats[key]}**\n"

        await send_embed_message(ctx, msg, author_icon_link=profile.member.avatar_url, author_name=profile.member.name)

    @commands.command()
    async def shop(self, ctx, page : int):
        pass
    
    @commands.command()
    async def hunt(self, ctx):
        ctx.send("Currently working on PVE Gameplay. Meanwhile, go h!challenge some people to earn some HutCoin")

    @commands.command()
    async def challenge(self, ctx, userToChallenge: discord.Member = None):
        if ctx.channel.id in self.games:
            await ctx.send(self.game_information["game_is_already_commencing_text"])
            return
        
        if userToChallenge == ctx.message.author:
            await ctx.send(self.game_information["challenging_self_text"])
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
                        self.games.update({ctx.channel.id: GladiatorGame(
                            ctx.message.author, userToChallenge)})

                        profiles = [GladiatorProfile(
                            ctx.message.author), GladiatorProfile(userToChallenge)]

                        crr_game = self.games[ctx.channel.id]
                        for profile in profiles:
                            for equipment in profile.profile_stats["Inventory"]:
                                crr_game.current_player.equip_item(
                                    equipment["id"], equipment["equipment_slot_id"])
                            crr_game.current_player.buff(
                                GladiatorStats(profile.profile_stats["boosts"]))
                            crr_game.switch_turns()

                        await send_embed_message(ctx, self.game_information["game_began_text"])
                        await self.gladiator_game_loop(ctx)

                    else:
                        await ctx.send(self.game_information["game_challenge_declined_text"].format(user.mention), delete_after=10)

                except asyncio.TimeoutError:
                    pass
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

            dmg_per_turn = game.current_player.take_damage_per_turn()
            if dmg_per_turn:
                await send_embed_message(ctx, dmg_per_turn)

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
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
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
                loser_profile = GladiatorProfile(game.current_player.Member)
                winner_profile = GladiatorProfile(game.players[1].Member)

                await send_embed_message(ctx, content=winner_profile.update_games(loser_profile.get_level(), won=True), author_name=winner_profile.member.name, author_icon_link=winner_profile.member.avatar_url)
                await send_embed_message(ctx, content=loser_profile.update_games(winner_profile.get_level(), won=False), author_name=loser_profile.member.name, author_icon_link=loser_profile.member.avatar_url)
                await send_embed_message(ctx, content=winner_profile.reward_player(loser_profile.get_level()), author_icon_link=winner_profile.member.avatar_url, author_name=winner_profile.member.name)
                
                del self.games[ctx.channel.id]
        else:
            await ctx.send(self.game_information["game_over_text"].format(game.current_player, game.current_player))
            loser_profile = GladiatorProfile(game.current_player.Member)
            winner_profile = GladiatorProfile(game.players[1].Member)

            await send_embed_message(ctx, content=winner_profile.update_games(loser_profile.get_level(), won=True), author_name=winner_profile.member.name, author_icon_link=winner_profile.member.avatar_url)
            await send_embed_message(ctx, content=loser_profile.update_games(winner_profile.get_level(), won=False), author_name=loser_profile.member.name, author_icon_link=loser_profile.member.avatar_url)
            await send_embed_message(ctx, content=winner_profile.reward_player(loser_profile.get_level()), author_icon_link=winner_profile.member.avatar_url, author_name=winner_profile.member.name)
                
            del self.games[ctx.channel.id]


def setup(bot):
    bot.add_cog(Gladiator(bot))
