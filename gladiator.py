import json
import os
import random
import asyncio
import discord

from discord.ext import commands
from Gladiator.Player import GladiatorNPC, GladiatorPlayer
from Gladiator.GladiatorGame import GladiatorGame, GladiatorStats
from Gladiator.Equipments.GladiatorEquipments import GladiatorEquipments
from Gladiator.AttackInformation.GladiatorAttackInformation import GladiatorAttackInformation
from Gladiator.Profile import GladiatorProfile
from util import send_embed_message


class Gladiator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # dictionary holding the id of the channel and the Game instance of the channel
        self.games = {}

        self.GladiatorEquipments = GladiatorEquipments()
        self.GladiatorAttackInformation = GladiatorAttackInformation()

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            self.settings = json.load(f)

        self.game_information = self.settings["game_information_texts"]

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

        await send_embed_message(ctx, str(profile), author_icon_link=profile.member.avatar_url, author_name=profile.member.name)

    @commands.command()
    async def shop(self, ctx, *page):
        if not page:
            slots = self.GladiatorEquipments.get_all_slots()
            msg = ""
            for slot in slots:
                msg += f"**Page {slot['id']} : {slot['Slot Name']}**\n"
            await send_embed_message(ctx, msg)
            return

        try:
            page_id = int(list(page)[0])
        except ValueError:
            await ctx.send(f"Couldn't find any page called {list(page)[0]}")
            return

        equipment_field_list, emoji_list = GladiatorGame.construct_shop_message(
            page_id)

        if equipment_field_list and emoji_list:
            msg = await send_embed_message(ctx, field_list=equipment_field_list)
            for emoji in emoji_list:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.message.author and reaction.message.id == msg.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=180.0, check=check)
                equipment_id = self.GladiatorEquipments.get_equipment_id_by_emoji(
                    reaction.emoji, page_id)
                await ctx.send(GladiatorProfile(ctx.message.author).buy_equipment(equipment_id))

            except asyncio.TimeoutError:
                await msg.delete()

    @commands.command()
    async def hunt(self, ctx):
        if ctx.channel.id in self.games:
            await ctx.send(self.game_information["game_is_already_commencing_text"])
            return

        roll = random.randint(0, 100)
        profile = GladiatorProfile(ctx.message.author)
        if self.settings["finding_npc_chance"] > roll:
            random_spawn, spawn_type = GladiatorGame.hunt()
            message = self.game_information["npc_spawned_text"].format(
                random_spawn.level, random_spawn.name, spawn_type["Spawn Type"])
            msg = await send_embed_message(ctx, content=message, image_url=random_spawn.image_path, image_local_file=True)
            await msg.add_reaction("⚔️")
            await msg.add_reaction("🏃")

            def check(reaction, user):
                return user == ctx.message.author and reaction.message.id == msg.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                if reaction.emoji == '⚔️':
                    self.games.update({ctx.channel.id: GladiatorGame(
                        GladiatorPlayer(ctx.message.author), random_spawn, spawn_type)})
                    crr_game = self.games[ctx.channel.id]
                    equip_inf = f"{crr_game.current_player} equips "
                    for equipment in profile.profile_stats["Inventory"]:
                        crr_game.current_player.equip_item(
                            equipment["id"], equipment["equipment_slot_id"])
                        try:
                            unlock_attack = equipment["unlock_attack_id"]
                            crr_game.current_player.unlock_attack_type(unlock_attack)
                        except KeyError:
                            pass

                        equip_inf += f"**{equipment['name']}** "
                    await ctx.send(equip_inf)
                    crr_game.current_player.buff(
                        GladiatorStats(profile.profile_stats["boosts"]))

                    # await send_embed_message(ctx, self.game_information["game_began_text"])
                    await self.gladiator_game_loop(ctx)
                else:
                    await self.hunt(ctx)

            except asyncio.TimeoutError:
                return
        else:
            msg = GladiatorGame.hunt_failed(
                GladiatorProfile(ctx.message.author))
            await send_embed_message(ctx, content=msg)

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
                        self.games.update({ctx.channel.id: GladiatorGame(GladiatorPlayer(
                            ctx.message.author), GladiatorPlayer(userToChallenge))})

                        profiles = [GladiatorProfile(
                            ctx.message.author), GladiatorProfile(userToChallenge)]

                        crr_game = self.games[ctx.channel.id]
                        for profile in profiles:
                            equip_inf = f"{crr_game.current_player} equips "
                            for equipment in profile.profile_stats["Inventory"]:
                                crr_game.current_player.equip_item(
                                    equipment["id"], equipment["equipment_slot_id"])
                            try:
                                unlock_attack = equipment["unlock_attack_id"]
                                crr_game.current_player.unlock_attack_type(unlock_attack)
                            except KeyError:
                                pass
                            
                            equip_inf += f"**{equipment['name']}** "
                            
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
            dmg_per_turn = game.current_player.take_damage_per_turn()
            if dmg_per_turn:
                await send_embed_message(ctx, dmg_per_turn)              
            if isinstance(game.current_player, GladiatorPlayer):
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
                    return user == game.current_player.member and reaction.message.id == attack_msg.id

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
                    # means that this is a duel between players
                    if isinstance(game.players[1], discord.Member):
                        await ctx.send(self.game_information["game_end_via_timeout_text"].format(game.players[1]))
                        loser_profile = GladiatorProfile(game.current_player.member)
                        winner_profile = GladiatorProfile(game.players[1].member)
                        winner_msg = winner_profile.update_games(loser_profile.get_level(), won=True)

                        await send_embed_message(ctx, content=winner_msg, author_name=winner_profile.member.name, author_icon_link=winner_profile.member.avatar_url)
                        await send_embed_message(ctx, content=loser_profile.update_games(winner_profile.get_level(), won=False), author_name=loser_profile.member.name, author_icon_link=loser_profile.member.avatar_url)
                    # this means the current player is non NPC and timedout
                    else:
                        await ctx.send(self.game_information["game_end_via_timeout_text"].format(game.players[1].name))

                    del self.games[ctx.channel.id]

            elif isinstance(game.current_player, GladiatorNPC):
                attack = game.current_player.get_random_attack()
                await send_embed_message(ctx, game.attack(attack["id"], attack["damage_type_id"])) 
                await self.gladiator_game_loop(ctx)
        else:
            #this means it is a pvp game and it ended
            if isinstance(game.current_player, GladiatorPlayer) and isinstance(game.players[1], GladiatorPlayer):
                await ctx.send(self.game_information["game_over_text"].format(game.current_player, game.current_player))
                loser_profile = GladiatorProfile(game.current_player.member)
                winner_profile = GladiatorProfile(game.players[1].member)
                winner_msg = winner_profile.update_games(loser_profile.get_level(), won=True)

                await send_embed_message(ctx, content=winner_msg, author_name=winner_profile.member.name, author_icon_link=winner_profile.member.avatar_url)
                await send_embed_message(ctx, content=loser_profile.update_games(winner_profile.get_level(), won=False), author_name=loser_profile.member.name, author_icon_link=loser_profile.member.avatar_url)
            # this means the current_player is an npc and he is dead, so reward the non NPC player
            elif isinstance(game.current_player, GladiatorNPC):
                winner_profile = GladiatorProfile(game.players[1].member)
                msg = winner_profile.update_games(game.current_player.level, won=True, XP=game.bonus_awards["XP"], HutCoins=game.bonus_awards["HutCoins"]) 
                await send_embed_message(ctx, content=msg, author_name=winner_profile.member.name, author_icon_link=winner_profile.member.avatar_url)
            # this means the current player is non NPC and dead
            else:
                loser_profile = GladiatorProfile(game.current_player.member)
                await send_embed_message(ctx, loser_profile.update_games(game.players[1].level, won=False))

            del self.games[ctx.channel.id]


def setup(bot):
    bot.add_cog(Gladiator(bot))
