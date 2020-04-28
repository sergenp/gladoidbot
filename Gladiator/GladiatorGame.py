import sys
sys.path.append('..')
import os
import collections
import random
import json

from Gladiator.Stats.GladiatorStats import GladiatorStats
from Gladiator.Player import GladiatorPlayer, GladiatorNPC
from Gladiator.Equipments.GladiatorEquipments import GladiatorEquipments
from Gladiator.AttackInformation.GladiatorAttackInformation import GladiatorAttackInformation
from Gladiator.Profile import GladiatorProfile
from Gladiator.NPCs.NPCFinder import NPCFinder



class GladiatorGame:
    def __init__(self, players: [GladiatorPlayer or GladiatorNPC], spawn_type: dict = None, **kwargs):
        self.current_player = players[0]
        self.next_player = players[-1]
        self.players = collections.deque(players)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", "GladiatorGameSettings.json")) as f:
            self.random_event_chance = json.load(f)["random_event_chance"]  # percent of random event chance

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Events", "Events.json")) as f:
            self.events = json.load(f)

        self.game_continues = True
        
        if spawn_type:
            self.bonus_awards = spawn_type["Spawn Bonuses"]

    def switch_turns(self):
        self.current_player = self.players.pop()
        self.next_player = self.players[-1]
        self.players.appendleft(self.current_player)

    def next_turn(self):
        turn_messages = []
        # switch the current players
        self.switch_turns()
        dmg_per_turn = self.current_player.take_damage_per_turn()
        if dmg_per_turn:
            turn_messages.append(dmg_per_turn)

        rand_ev = self.random_event()
        if rand_ev:
            turn_messages.append(rand_ev)

        if self.current_player.dead:
            self.game_continues = False
        # return true because we successfully went to the other round, along with messages about the round
        return self.game_continues, turn_messages

    def attack(self, attack_name=""):
        return self.current_player.attack(self.next_player, attack_name)

    @staticmethod
    def construct_information_message(gladiator_profile: GladiatorProfile):
        settings = None
        attack_types = None
        damage_types = None
        gladiator_stats = gladiator_profile.get_stats()

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", "GladiatorGameSettings.json")) as f:
            settings = json.load(f)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            attack_types = json.load(f)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "AttackInformation", "GladiatorDamageTypes.json")) as f:
            damage_types = json.load(f)

        information_text = settings["game_information_texts"]["title_text"] + "\n"
        for k in gladiator_stats.keys():
            if "Chance" in k:
                information_text += f"{k} = %{gladiator_stats[k]}\n"
            else:
                information_text += f"{k} = {gladiator_stats[k]}\n"

        information_text += "\n" + settings["game_information_texts"]["information_about_attack_types_text"].format(
            len(attack_types))
        for i in attack_types:
            information_text += f"\n***{i['name']}*** has these bonuses:\n"
            information_text += f"Damage Type : **{i['damage_type_name']}**\n"
            for k in i["buffs"].keys():
                if "Chance" in k:
                    information_text += f"{k} : **%{i['buffs'][k]}**\n"
                else:
                    information_text += f"{k} : **{i['buffs'][k]}**\n"

        information_text += "\n" + settings["game_information_texts"]["damage_types_info"].format(
            len(damage_types))
        for i in damage_types:
            information_text += f"**\n{i['damage_type_name']}** : {i['description']}\n"

        return information_text

    @staticmethod
    def get_event(event_dict, player_to_be_affected: (GladiatorNPC, GladiatorPlayer, GladiatorProfile)):
        if isinstance(player_to_be_affected, GladiatorNPC):
            return ""

        event_text = event_dict["event_text"].format(player_to_be_affected.member.mention)
        event_buffs = event_dict["event_buffs"]
        event_info = "\n" + event_text + "\n"

        if list(event_dict["event_type"])[0] == "Profile":
            profile = None
            if isinstance(player_to_be_affected, GladiatorProfile):
                profile = player_to_be_affected

            else:
                profile = GladiatorProfile(player_to_be_affected.member)
            
            for k in event_buffs.keys():
                event_info += profile.event_bonus(k, event_buffs[k]) + "\n"
                
        elif list(event_dict["event_type"])[0] == "PVP":
            if isinstance(player_to_be_affected, GladiatorPlayer):
                if event_buffs:
                    buff = GladiatorStats(event_buffs)
                    player_to_be_affected.buff(buff)
                    event_info += str(buff)

                if event_dict["event_type"]["PVP"] == "unlock_attack_type":
                    player_to_be_affected.unlock_attack_type(
                        event_dict["attack_name"])
            
        return "--------------------------\n" + event_info + "\n--------------------------"
    

    def random_event(self):
        if not self.game_continues:
            return ""
        roll = random.randint(0, 100)
        if self.random_event_chance > roll:
            event = random.choice(self.events)
            player_to_be_affected = random.choice(self.players)
            return GladiatorGame.get_event(event, player_to_be_affected)
    
    @staticmethod
    def hunt():
        spawns = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "NPCs", "Settings", "Spawns.json")))
        # roll for spawn
        roll = random.randint(0, 100) #
        spawn_type = spawns[0]
        for spawn in spawns:
            if roll < spawn["Spawn Chance"]:
                spawn_type = spawn
        # get a random json file from NPCs directory given spawn type
        npc_stats_path = NPCFinder().get_npc_by_name(random.choice(spawn_type["NPCs"]))
        # return a GladiatorNPC with the name of the json file, and the stats it has
        return GladiatorNPC(stats_path=npc_stats_path), spawn_type
        
    @staticmethod
    def construct_shop_message(page_name: int):
        equipments = GladiatorEquipments().get_all_equipments_from_slot_name(page_name)
        equipment_field_list = []
        emoji_list = []
        for k in equipments:
            value = ""
            for val in k["buffs"].keys():
                if "Chance" in val:
                    value += f"{val} : **%{k['buffs'][val]}**\n"
                else:
                    value += f"{val} : **{k['buffs'][val]}**\n"
            value += f"Price : **{k['price']} HutCoins**\n"

            debuff = GladiatorAttackInformation().find_turn_debuff(k["debuff_name"])
            if debuff:
                for j in debuff["debuff_stats"]:
                    if "Chance" in j:
                        value += f"{j} : **%{debuff['debuff_stats'][j]}**\n"
                    else:
                        value += f"{j} : **{debuff['debuff_stats'][j]}**\n"
            try:
                attack = GladiatorAttackInformation().find_attack_type(k["unlock_attack_name"])
                if attack:
                    value += f"Unlocks {attack['name']} {attack['reaction_emoji']}\n"
            except KeyError:
                pass

            name = f"{k['name']} {k['reaction_emoji']}"
            emoji_list.append(k["reaction_emoji"])
            dct = {
                "name": name,
                "value": value,
                "inline": True
            }
            equipment_field_list.append(dct)
            
        return equipment_field_list, emoji_list
