import json
import os
import asyncio
import discord
from datetime import datetime
import textwrap
import pathlib
from discord.ext import commands
from Gladiator.Player import GladiatorNPC, GladiatorPlayer
from Gladiator.GladiatorGame import GladiatorGame
from Gladiator.Equipments.GladiatorEquipments import GladiatorEquipments
from Gladiator.AttackInformation.GladiatorAttackInformation import GladiatorAttackInformation
from Gladiator.MatchMessages import MatchMessages
from Gladiator.Profile import GladiatorProfile
from .util import send_embed_message

path = pathlib.Path(__file__).parent.absolute()

class Gladiator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # dictionary holding the id of the channel and the Game instance of the channel
        self.games = {}

        self.GladiatorEquipments = GladiatorEquipments()
        self.GladiatorAttackInformation = GladiatorAttackInformation()

        with open(path / ".." / "Gladiator" / "Settings" / "GladiatorGameSettings.json", "r") as f:
            self.settings = json.load(f)

        self.game_information = self.settings["game_information_texts"]

    @commands.command()
    async def gamead(self, ctx):
        await ctx.send(self.game_information["game_ad_text"])

    @commands.command()
    async def gamerules(self, ctx):
        channel = await ctx.message.author.create_dm()
        for line in textwrap.wrap(GladiatorGame.construct_information_message(GladiatorProfile(ctx.message.author)),
                                  width=1200, replace_whitespace=False, expand_tabs=False, drop_whitespace=False,
                                  placeholder="...", fix_sentence_endings=True, break_long_words=False):
            await send_embed_message(channel, line)

    @commands.command()
    async def profile(self, ctx, userProfileToDisplay: discord.Member = None):
        profile = None
        if userProfileToDisplay:
            profile = GladiatorProfile(userProfileToDisplay)
        else:
            profile = GladiatorProfile(ctx.message.author)

        await send_embed_message(ctx, str(profile), author_icon_link=profile.member.avatar_url,
                                 author_name=profile.member.name)

    def create_game(self, channel_id, players, spawn_type=None):
        self.games.update({
            channel_id:
                {
                    "Game": GladiatorGame(players, spawn_type=spawn_type),
                    "Game Messages": MatchMessages(players, datetime.now())
                }
        })

    @commands.command()
    async def shop(self, ctx, *page):
        slots = self.GladiatorEquipments.get_all_slots()
        if not page:
            msg = ""
            for k, slot in enumerate(slots):
                msg += f"**Page {k + 1} : {slot['Slot Name']}**\n"
            await send_embed_message(ctx, msg)
            return

        try:
            page_id = int(list(page)[0])
            page_name = slots[page_id - 1]["Slot Name"]
        except (ValueError, IndexError):
            await ctx.send(f"Couldn't find page {list(page)[0]}")
            return

        equipment_field_list, emoji_list = GladiatorGame.construct_shop_message(page_name)

        if equipment_field_list and emoji_list:
            msg = await send_embed_message(ctx, field_list=equipment_field_list)
            for emoji in emoji_list:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.message.author and reaction.message.id == msg.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                equipment_name = self.GladiatorEquipments.get_equipment_name_by_emoji(reaction.emoji, page_name)
                await ctx.send(GladiatorProfile(ctx.message.author).buy_equipment(equipment_name))

            except asyncio.TimeoutError:
                await msg.delete()

    @commands.command()
    async def hunt(self, ctx):
        if ctx.channel.id in self.games:
            await ctx.send(self.game_information["game_is_already_commencing_text"])
            return

        profile = GladiatorProfile(ctx.message.author)
        random_spawn, spawn_type = GladiatorGame.hunt()
        message = self.game_information["npc_spawned_text"].format(
            random_spawn.level, random_spawn.name, spawn_type["Spawn Type"])
        msg = await send_embed_message(ctx, content=message, image_url=random_spawn.image_path, footer_text=random_spawn.footer_text)
        await msg.add_reaction("⚔️")
        await msg.add_reaction("🏃")

        def check(reaction, user):
            return user == ctx.message.author and reaction.message.id == msg.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
            if reaction.emoji == '⚔️':
                self.create_game(ctx.channel.id, [GladiatorPlayer(ctx.message.author), random_spawn],
                                 spawn_type=spawn_type)
                crr_game = self.games[ctx.channel.id]["Game"]
                if len(profile.profile_stats["Inventory"]) > 0:
                    equip_inf = f"{crr_game.current_player} equips "
                    for equipment in profile.profile_stats["Inventory"]:
                        crr_game.current_player.equip_item(equipment["name"], equipment["type"])
                        equip_inf += f"**{equipment['name']}** "
                    await ctx.send(equip_inf)
                    self.games[ctx.channel.id]["Game Messages"].add_msg(equip_inf)
                await self.gladiator_game_loop(ctx)
            else:
                await self.hunt(ctx)

        except asyncio.TimeoutError:
            await msg.delete()
            return

    @commands.command()
    async def challenge(self, ctx, userToChallenge: discord.Member = None):
        if ctx.channel.id in self.games:
            await ctx.send(self.game_information["game_is_already_commencing_text"])
            return

        if userToChallenge:
            if userToChallenge.bot:
                await ctx.send(self.game_information["game_challenge_bot_text"].format(ctx.message.author.mention))
                return

            if userToChallenge == ctx.message.author:
                await ctx.send(self.game_information["challenging_self_text"])
                return

            msg = await ctx.send(self.game_information["game_challenge_text"].format(
                ctx.message.author.mention, userToChallenge.mention, '👍', '👎'), delete_after=20.0)
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')

            def check(reaction, user):
                return user == userToChallenge and reaction.message.id == msg.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
                if reaction.emoji == '👍':
                    profiles = [GladiatorProfile(
                        ctx.message.author), GladiatorProfile(userToChallenge)]
                    player1 = GladiatorPlayer(ctx.message.author)
                    player2 = GladiatorPlayer(userToChallenge)
                    self.create_game(ctx.channel.id, [player1, player2])

                    crr_game = self.games[ctx.channel.id]["Game"]
                    for profile in profiles:
                        if profile.profile_stats["Inventory"]:
                            equip_inf = f"{crr_game.current_player} equips "
                            for equipment in profile.profile_stats["Inventory"]:
                                crr_game.current_player.equip_item(equipment["name"], equipment["type"])
                                equip_inf += f"**{equipment['name']}** "
                            await ctx.send(equip_inf)
                            self.games[ctx.channel.id]["Game Messages"].add_msg(equip_inf)
                        crr_game.switch_turns()

                    await send_embed_message(ctx, self.game_information["game_began_text"])
                    await self.gladiator_game_loop(ctx)

                else:
                    await ctx.send(self.game_information["game_challenge_declined_text"].format(user.mention),
                                   delete_after=10)

            except asyncio.TimeoutError:
                pass
            else:
                pass

        else:
            await ctx.send(
                self.game_information["game_challenge_user_mention_missing"].format(ctx.message.author.mention))

    async def gladiator_game_loop(self, ctx):
        game = self.games[ctx.channel.id]["Game"]
        game_messages = self.games[ctx.channel.id]["Game Messages"]
        game_continues, messages = game.next_turn()
        if game_continues:
            for msg in messages:
                await send_embed_message(ctx, msg)
                game_messages.add_msg(msg)

            if isinstance(game.current_player, GladiatorPlayer):
                attack_msg_text = self.game_information["game_turn_text"].format(
                    game.current_player)

                for i in game.current_player.permitted_attacks:
                    attack_msg_text += f"{i['name']} : {i['reaction_emoji']}\n"

                attack_msg = await send_embed_message(ctx, attack_msg_text)

                for i in game.current_player.permitted_attacks:
                    await attack_msg.add_reaction(i["reaction_emoji"])

                def check(reaction, user):
                    return user == game.current_player.member and reaction.message.id == attack_msg.id

                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
                    msg = ""
                    for i in game.current_player.permitted_attacks:
                        if i["reaction_emoji"] == reaction.emoji:
                            msg = game.attack(i["name"])
                            break
                    else:
                        msg = game.attack()

                    await send_embed_message(ctx, msg)
                    game_messages.add_msg(msg)
                    await attack_msg.delete()
                    await self.gladiator_game_loop(ctx)

                except asyncio.TimeoutError:
                    msg = self.game_information["game_end_via_timeout_text"]
                    await ctx.send(msg)
                    game_messages.add_msg(msg)
                    game_messages.save()
                    del self.games[ctx.channel.id]

            elif isinstance(game.current_player, GladiatorNPC):
                atk = game.current_player.get_random_attack()
                msg = game.attack(atk["name"])
                await send_embed_message(ctx, msg)
                game_messages.add_msg(msg)
                await self.gladiator_game_loop(ctx)
        else:
            # this means it is a pvp game and it ended
            if isinstance(game.current_player, GladiatorPlayer) and isinstance(game.players[1], GladiatorPlayer):
                await ctx.send(self.game_information["game_over_text"].format(game.current_player, game.current_player))
                loser_profile = GladiatorProfile(game.current_player.member)
                winner_profile = GladiatorProfile(game.players[1].member)
                winner_msg = winner_profile.member.name + " " + winner_profile.update_games(loser_profile.get_level(),
                                                                                            won=True)
                loser_msg = loser_profile.member.name + " " + loser_profile.update_games(winner_profile.get_level(),
                                                                                         won=False)
                await send_embed_message(ctx, content=winner_msg, author_name=winner_profile.member.name,
                                         author_icon_link=winner_profile.member.avatar_url)
                await send_embed_message(ctx, content=loser_msg, author_name=loser_profile.member.name,
                                         author_icon_link=loser_profile.member.avatar_url)
                game_messages.add_msg([winner_msg, loser_msg])

            # this means the current_player is an npc and he is dead, so reward the non NPC player
            elif isinstance(game.current_player, GladiatorNPC):
                winner_profile = GladiatorProfile(game.players[1].member)
                msg = winner_profile.update_games(game.current_player.level, won=True, XP=game.bonus_awards["XP"],
                                                  HutCoins=game.bonus_awards["HutCoins"])
                await send_embed_message(ctx, content=msg, author_name=winner_profile.member.name,
                                         author_icon_link=winner_profile.member.avatar_url)
                game_messages.add_msg(msg)
            # this means the current player is non NPC and dead
            else:
                loser_profile = GladiatorProfile(game.current_player.member)
                msg = loser_profile.update_games(game.next_player.level, won=False)
                await send_embed_message(ctx, msg)
                game_messages.add_msg(msg)

            game_messages.save()
            del self.games[ctx.channel.id]


def setup(bot):
    bot.add_cog(Gladiator(bot))
