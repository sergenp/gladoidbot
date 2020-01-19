from GladiatorPlayer import GladiatorPlayer, AttackTypes
from GladiatorStats import GladiatorArmor, GladiatorSword, GladiatorBuff
import random
import json
import collections


class GladiatorGame:
    def __init__(self, player1, player2):
        self.player1 = GladiatorPlayer(player1)
        self.player2 = GladiatorPlayer(player2)
        self.random_event_chance = 40  # percent of random event chance
        self.current_player = self.player1
        self.players = collections.deque([self.player1, self.player2])
        with open("GladiatorEvents.json") as file:
            self.events = json.load(file)

    def next_turn(self):
        # switch the current players
        self.players.appendleft(self.players.pop())
        self.current_player = self.players[0]
        # return if the current_player is dead
        if self.current_player.dead:
            return False
        # return true because we successfully went to the other round
        return True

    def attack(self, attackType: AttackTypes):
        return self.players[0].attack(self.players[1], attackType)

    def random_event(self):
        roll = random.randint(0, 100)
        event_happened = self.random_event_chance > roll
        if event_happened:
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
            return "**" + event_info + "**"

        return ""
