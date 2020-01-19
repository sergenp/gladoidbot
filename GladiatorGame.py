from GladiatorPlayer import GladiatorPlayer
from GladiatorStats import GladiatorArmor, GladiatorSword, GladiatorBuff
import random
import json


class GladiatorGame:
    def __init__(self, player1, player2):
        self.player1 = GladiatorPlayer(player1)
        self.player2 = GladiatorPlayer(player2)
        self.random_event_chance = 40  # percent of random event chance
        self.__round_count = 1
        self.__turn = self.player1
        with open("GladiatorEvents.json") as file:
            self.events = json.load(file)

    def next_turn(self):
        if self.__round_count % 2 == 0:
            self.__turn = self.player2
        else:
            self.__turn = self.player1
        self.__round_count += 1
        return self.random_event()

    def random_event(self):
        roll = random.randint(0, 100)
        if self.random_event_chance > roll:
            event = random.choice(self.events)
            player_to_be_affected = random.choice([self.player1, self.player2])
            event_text = event["event_text"].format(player_to_be_affected.name)
            event_buffs = event["event_buffs"]
            event_info = event_text

            if event["event_type"] == "buff":
                buff = GladiatorBuff(event_buffs)
                player_to_be_affected.buff(buff)
                event_info += " " + str(buff)
            elif event["event_type"] == "sword_equipment":
                sword_equipment = GladiatorSword(event_buffs)
                player_to_be_affected.equip_sword(sword_equipment)
                event_info += " " + str(sword_equipment)
            elif event["event_type"] == "armor_equipment":
                armor_equipment = GladiatorArmor(event_buffs)
                player_to_be_affected.equip_armor(armor_equipment)
                event_info += " " + str(armor_equipment)

            return event_info
