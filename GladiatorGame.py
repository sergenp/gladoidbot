import json
import random
import collections
import os
from GladiatorPlayer import GladiatorPlayer
from GladiatorStats import GladiatorArmor, GladiatorSword, GladiatorBuff


class GladiatorGame:
    def __init__(self, player1, player2):
        self.player1 = GladiatorPlayer(player1)
        self.player2 = GladiatorPlayer(player2)
        self.current_player = self.player1
        self.players = collections.deque([self.player1, self.player2])
        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            self.game_settings = json.load(f)  # percent of random event chance
        self.random_event_chance = self.game_settings["random_event_chance"]
        with open(os.path.join("Gladiator", "Events", "GladiatorEvents.json")) as f:
            self.events = json.load(f)
        self.game_continues = True

    def next_turn(self):
        # switch the current players
        self.players.appendleft(self.players.pop())
        self.current_player = self.players[0]
        # return if the current_player is dead
        if self.current_player.dead:
            self.game_continues = False
        # return true because we successfully went to the other round
        return self.game_continues

    def attack(self, attackType_id=0, damage_type_id=0):
        return self.players[0].attack(self.players[1], attackType_id, damage_type_id)

    @staticmethod
    def construct_information_message():
        settings = None
        attack_types = None
        damage_types = None

        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            settings = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            attack_types = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorDamageTypes.json")) as f:
            damage_types = json.load(f)

        information_text = settings["game_information_texts"]["title_text"]
        for k in settings["Gladiator_initial_stats"].keys():
            information_text += f"{k}={settings['Gladiator_initial_stats'][k]}\n"

        information_text += settings["game_information_texts"]["information_about_attack_types_text"].format(
            len(attack_types))
        for i in attack_types:
            information_text += f"{i['name']} has these stats:\n"
            information_text += f"**Damage Type : {i['damage_type_name']}**\n"
            for k in i["buffs"].keys():
                information_text += f"**{k} : {i['buffs'][k]}**\n"

        information_text += settings["game_information_texts"]["damage_types_info"].format(
            len(damage_types))
        for i in damage_types:
            information_text += f"**{i['damage_type_name']}** : {i['description']}\n"

        return information_text

    def random_event(self):
        if not self.game_continues:
            return ""
        roll = random.randint(0, 100)
        if self.random_event_chance > roll:
            event = random.choice(self.events)
            player_to_be_affected = random.choice([self.player1, self.player2])
            event_text = event["event_text"].format(player_to_be_affected)
            event_buffs = event["event_buffs"]
            event_info = event_text + "\n"

            if event["event_type"] == "buff" or event["event_type"] == "debuff":
                buff = GladiatorBuff(event_buffs)
                player_to_be_affected.buff(buff)
                event_info += str(buff)
            elif event["event_type"] == "sword_equipment":
                sword_equipment = GladiatorSword(event_buffs)
                player_to_be_affected.equip_sword(sword_equipment)
                event_info += str(sword_equipment)
            elif event["event_type"] == "armor_equipment":
                armor_equipment = GladiatorArmor(event_buffs)
                player_to_be_affected.equip_armor(armor_equipment)
                event_info += str(armor_equipment)
            elif event["event_type"] == "unlock_attack_type":
                player_to_be_affected.unlock_attack_type(event["attack_id"])
                if event_buffs:
                    buff = GladiatorBuff(event_buffs)
                    player_to_be_affected.buff(buff)
                    event_info += str(buff)

            return "*--------------------------\n" + event_info + "\n--------------------------*"
        else:
            return ""
