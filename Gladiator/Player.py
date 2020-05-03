import random
import math
import json
import os
from Gladiator.Stats.GladiatorStats import GladiatorStats
from Gladiator.AttackInformation.GladiatorAttackInformation import GladiatorAttackInformation
from Gladiator.Equipments.GladiatorEquipments import GladiatorEquipments


INITIAL_ATTACK_TYPES_COUNT = 3


class Player:
    def __init__(self, stats_path):
        self.dead = False
        self.debuffs = []
        self.permitted_attacks = []
        self.json_dict = json.load(open(stats_path, "r"))
        self.stats = GladiatorStats(self.json_dict["Stats"])
        self.attack_information = GladiatorAttackInformation()
        self.information = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", "GladiatorGameSettings.json"), "r"))["game_information_texts"]

    def take_damage(self, damage, damage_type):
        try:
            dmg = damage - self.stats[damage_type["armor_type_that_absorbs"]]
        except KeyError:
            dmg = damage

        # check if the damage is blocked
        roll = random.randint(0, 100)
        if self.stats["Block Chance"] > roll or dmg <= 0:
            return self.information["block_damage_text"].format(self)

        dmg = round(dmg, 2)
        self.stats["Health"] = round(self.stats["Health"] - dmg, 2)
        if self.stats["Health"] <= 0:
            return self.die()
        # return info
        return self.information["take_damage_text"].format(self, dmg, self, self.stats['Health'])

    def damage_enemy(self, otherPlayer, damage_type_name=""):
        inf = ""
        # roll to see if attack hit
        roll = random.randint(0, 100)
        if self.stats["Attack Chance"] < roll:
            return self.information["dodge_text"].format(otherPlayer)

        dmg_type = self.attack_information.find_damage_type(damage_type_name)

        min_dmg = self.stats[dmg_type["min_damage_stat"]]
        max_dmg = self.stats[dmg_type["max_damage_stat"]]

        # roll for damage
        dmg = random.randint(min_dmg, max_dmg)

        # roll for critical damage
        crit_roll = random.randint(0, 100)
        try:
            if self.stats["Debuff Chance"] > 0:
                # roll for debuff effect to other player
                if self.stats["Debuff Chance"] > random.randint(0, 100):
                    inf += otherPlayer.take_debuff(self.stats["Debuff Type"])
        except KeyError:
            pass

        if self.stats["Critical Damage Chance"] > crit_roll:
            crit_dmg = math.ceil(dmg * self.stats["Critical Damage Boost"])
            return inf + self.information["critical_hit_text"] + otherPlayer.take_damage(crit_dmg, dmg_type)
       
        return inf + otherPlayer.take_damage(dmg, dmg_type)

    def attack(self, otherPlayer, attack_type_name=""):
        if not isinstance(otherPlayer, Player):
            raise ValueError(
                "otherPlayer must be an instance of Player")

        # find the attack corresponding the name
        attack = self.attack_information.find_attack_type(attack_type_name)
        if not attack:
            attack = random.choice(self.permitted_attacks)

        self.buff(attack["buffs"])
        inf = self.damage_enemy(otherPlayer, attack["damage_type_name"])
        self.buff(attack["buffs"], buff_type="debuff")
        return f"{self} Used {attack['name']} {attack['reaction_emoji']}\n" + inf


    def die(self):
        self.dead = True
        return random.choice(self.information["death_texts"]).format(self)

    def buff(self, buff: GladiatorStats or dict, buff_type="buff"):
        if buff_type == "buff":
            self.stats += buff
        elif buff_type == "debuff":
            self.stats -= buff

    def take_debuff(self, turn_debuff_name: str):

        debuff = self.attack_information.find_turn_debuff(turn_debuff_name)

        # if the given debuff is already affecting the player,
        # make it last more turns
        for dbf in self.debuffs:
            if dbf["debuff_stats"]["Debuff Type"] == debuff["debuff_stats"]["Debuff Type"]:
                dbf["lasts_turn_count"] += 1
                break
        # if given debuff is not currently affecting the player,
        # append it to the current debuffs list
        else:
            self.debuffs.append(debuff)

        return self.information["take_debuff_text"].format(self, debuff["debuff_stats"]["Debuff Type"], debuff["lasts_turn_count"])

    def take_damage_per_turn(self):
        # if there is any debuffs in the list
        if len(self.debuffs) > 0:
            inf = ""
            for index, debuff in enumerate(self.debuffs):
                if debuff["lasts_turn_count"] > 0:
                    debuff["lasts_turn_count"] -= 1
                    self.stats['Health'] -= debuff["debuff_stats"]["Debuff Damage"]
                    inf += self.information["take_damage_per_turn_from_debuffs_text"].format(
                        self, debuff["debuff_stats"]["Debuff Damage"], debuff["debuff_stats"]["Debuff Type"], self.stats["Health"], debuff["lasts_turn_count"])
                    
                    if self.stats["Health"] <= 0:
                        inf += "\n" + self.die()

                else:
                    del self.debuffs[index]

            return inf
        return ""


class GladiatorPlayer(Player):
    def __init__(self, member):
        super().__init__(stats_path=os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "UserProfileData", f"{member.id}.json"))
        self.member = member
        self.equipment_information = GladiatorEquipments()
        self.permitted_attacks = self.attack_information.attack_types[:INITIAL_ATTACK_TYPES_COUNT]

    def equip_item(self, equipment_name, equipment_slot_name):
        slot = self.equipment_information.find_slot(equipment_slot_name)
        # if there is an equipment equipped already in the slot,
        # do nothing, and return
        if slot:
            if slot["Equipment"]:
                return

            equipment = self.equipment_information.find_equipment(equipment_name)
            if equipment:
                if equipment["type"] == slot["Slot Name"]:
                    self.equipment_information.update_slot(slot["Slot Name"], equipment)
                    self.stats += equipment["buffs"]
                    if equipment["unlock_attack_name"]:
                        self.unlock_attack_type(equipment["unlock_attack_name"])
                    debuff = self.attack_information.find_turn_debuff(equipment["debuff_name"])
                    if debuff:
                        self.stats += debuff["debuff_stats"]

    def unlock_attack_type(self, attack_name):
        for i in self.permitted_attacks:
            if i["name"] == attack_name:
                return

        self.permitted_attacks.append(
            self.attack_information.find_attack_type(attack_name))

    def __repr__(self):
        return f"<@{self.member.id}>"


class GladiatorNPC(Player):
    def __init__(self, stats_path, **kwargs):
        super().__init__(stats_path)
        self.name = self.json_dict["Name"]
        self.image_path = f"https://thehutbotweb.herokuapp.com/npcimage?name={self.name}"
        self.level = random.randint(self.json_dict["Min Level"], self.json_dict["Max Level"])
        for attack_name in self.json_dict["Attacks"]:
            self.permitted_attacks.append(
                self.attack_information.find_attack_type(attack_name))

        for k, min_stat in dict(self.json_dict["Stats"]).items():
            for l in range(self.level):
                min_stat += (l/17)**1.1
                min_stat = round(min_stat, 2)
            self.stats[k] = min_stat

        for debuff_name in self.json_dict["Debuffs"]:
            self.stats += self.attack_information.find_turn_debuff(debuff_name)["debuff_stats"]
        
        self.stats += kwargs

    def get_random_attack(self):
        return random.choice(self.permitted_attacks)

    def __repr__(self):
        return f"Level {self.level} {self.name} "
