from GladiatorPlayer import GladiatorPlayer
from GladiatorStats import GladiatorArmor, GladiatorSword, GladiatorBuff
import random
import json
import collections


class GladiatorGame:
    def __init__(self, player1, player2):
        self.player1 = GladiatorPlayer(player1)
        self.player2 = GladiatorPlayer(player2)
        self.current_player = self.player1
        self.players = collections.deque([self.player1, self.player2])
        with open("GladiatorGameSettings.json") as f:
            self.random_event_chance = json.load(
                f)["random_event_chance"]  # percent of random event chance
        with open("GladiatorEvents.json") as file:
            self.events = json.load(file)
        self.game_continues = True

    def next_turn(self):
        # switch the current players
        self.players.appendleft(self.players.pop())
        self.current_player = self.players[0]
        # return if the current_player is dead
        if self.current_player.dead:
            self.game_continues = False
            return self.game_continues
        # return true because we successfully went to the other round
        return self.game_continues

    def attack(self, attackType_id):
        return self.players[0].attack(self.players[1], attackType_id)

    @staticmethod
    def construct_information_message():
        information_text = "**Every Gladiator starts the game with these stats:\n**"
        settings = None
        attack_types = None
        with open("GladiatorGameSettings.json") as f:
            settings = json.load(f)
        with open("GladiatorAttackBuffs.json") as f:
            attack_types = json.load(f)
        for k in settings["Gladiator_initial_stats"].keys():
            information_text += f"{k}={settings['Gladiator_initial_stats'][k]}\n"

        information_text += f"**There are {len(attack_types)} attacks available to each gladiator. Each gives you following bonuses:**\n"
        for i in attack_types:
            information_text += f"{i['name']} gives:\n"
            for k in i["buffs"].keys():
                information_text += f"**{k} : {i['buffs'][k]}**\n"
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

            if event["event_type"] == "buff":
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
            elif event["event_type"] == "debuff":
                debuff = GladiatorBuff(event_buffs)
                player_to_be_affected.buff(debuff)
                event_info += str(debuff)
            return "*--------------------------\n" + event_info + "\n--------------------------*"
        else:
            return ""
