import discord
from discord.ext import commands
import asyncio
from Gladiator.GladiatorGame import GladiatorGame
from util import send_embed_message
from enum import Enum
import json
import os

PLAYER_COUNT = 2


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
                        await msg.delete()
                        self.games.update({ctx.channel.id: GladiatorGame(
                            ctx.message.author, userToChallenge)})

                        for _ in range(0, PLAYER_COUNT):
                            try:
                                crr_game = self.games[ctx.channel.id]
                                for eq_slot in self.equipment_slots:
                                    await self.select_equipments(ctx, crr_game.current_player.Member, eq_slot["id"])
                                crr_game.switch_turns()
                            except KeyError:
                                return
                        await send_embed_message(ctx, self.game_information["game_began_text"])
                        await self.gladiator_game_loop(ctx)

                    else:
                        await ctx.send(self.game_information["game_challenge_declined_text"].format(user.mention), delete_after=10)

                    await msg.delete()

                except asyncio.TimeoutError:
                    await msg.delete()
                else:
                    pass

        else:
            await ctx.send(self.game_information["game_challenge_user_mention_missing"].format(ctx.message.author.mention))

    async def select_equipments(self, ctx, member, equipment_slot_id=0):
        try:
            game = self.games[ctx.channel.id]
        except KeyError:
            return
        await ctx.send(f"{member.mention} Please select your item")
        equipments = []
        for equipment in self.equipments:
            if equipment["equipment_slot_id"] == equipment_slot_id:
                equipments.append(equipment)

        equipment_field_list = []
        emoji_list = []
        for k in equipments:
            value = ""
            for val in k["buffs"].keys():
                value += f"{val} : {k['buffs'][val]}\n"

            if k["debuff_id"] != -1:
                for debuff in self.debuffs:
                    if debuff["debuff_stats"]["debuff_id"] == k["debuff_id"]:
                        for j in debuff["debuff_stats"]:
                            if j == "debuff_id":
                                continue
                            else:
                                value += f"{j} : {debuff['debuff_stats'][j]}\n"

            name = f"{k['name']} {k['reaction_emoji']}"
            emoji_list.append(k["reaction_emoji"])
            dct = {
                "name": name,
                "value": value,
                "inline": True
            }
            equipment_field_list.append(dct)
        msg = await send_embed_message(ctx, field_list=equipment_field_list)
        for emoji in emoji_list:
            await msg.add_reaction(emoji)

        def check(reaction, user):
            return user == member and reaction.message.id == msg.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            equipment_id = 0
            for eq in equipments:
                if eq["reaction_emoji"] == reaction.emoji:
                    equipment_id = eq["id"]
                    break

            game.current_player.equip_item(equipment_id, equipment_slot_id)
            await msg.delete()

        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("Player failed to choose an equipment, the duel is cancelled", delete_after=10)
            del self.games[ctx.channel.id]
            raise asyncio.TimeoutError

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
                del self.games[ctx.channel.id]
        else:
            await ctx.send(self.game_information["game_over_text"].format(game.current_player, game.current_player))
            del self.games[ctx.channel.id]


def setup(bot):
    bot.add_cog(Gladiator(bot))
