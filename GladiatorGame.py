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
            self.random_event_chance = json.load(
                f)["random_event_chance"]  # percent of random event chance

        with open(os.path.join("Gladiator", "Events", "GladiatorEvents.json")) as f:
            self.events = json.load(f)

        self.game_continues = True

    def select_sword_for_current_player(self, sword_id):
        self.current_player.equip_sword(sword_id)

    def select_armor_for_current_player(self, armor_id):
        self.current_player.equip_armor(armor_id)

    def switch_turns(self):
        self.players.appendleft(self.players.pop())
        self.current_player = self.players[0]

    def next_turn(self):
        # switch the current players
        self.switch_turns()
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
        initial_stats = None

        with open(os.path.join("Gladiator", "GladiatorStats.json")) as f:
            initial_stats = json.load(f)

        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            settings = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            attack_types = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorDamageTypes.json")) as f:
            damage_types = json.load(f)

        information_text = settings["game_information_texts"]["title_text"]
        for k in initial_stats["Gladiator_initial_stats"].keys():
            if "Chance" in k:
                information_text += f"{k}=%{initial_stats['Gladiator_initial_stats'][k]}\n"
            else:
                information_text += f"{k}={initial_stats['Gladiator_initial_stats'][k]}\n"

        information_text += settings["game_information_texts"]["information_about_attack_types_text"].format(
            len(attack_types))
        for i in attack_types:
            information_text += f"{i['name']} has these stats:\n"
            information_text += f"**Damage Type : {i['damage_type_name']}**\n"
            for k in i["buffs"].keys():
                if "Chance" in k:
                    information_text += f"**{k} : %{i['buffs'][k]}**\n"
                else:
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

            if event_buffs:
                buff = GladiatorBuff(event_buffs)
                player_to_be_affected.buff(buff)
                event_info += str(buff)

            if event["event_type"] == "unlock_attack_type":
                player_to_be_affected.unlock_attack_type(event["attack_id"])

            return "*--------------------------\n" + event_info + "\n--------------------------*"
        else:
            return ""
