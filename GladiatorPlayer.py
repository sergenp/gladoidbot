import random
import math
from GladiatorStats import GladiatorStats, GladiatorArmor, GladiatorSword, GladiatorBuff
from enum import Enum
import json
import os


class GladiatorPlayer:
    def __init__(self, member):
        self.Member = member
        self.id = self.Member.id
        self.stats = GladiatorStats()
        self.sword_equipped = None
        self.armor_equipped = None
        self.dead = False
        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            self.information = json.load(f)["game_information_texts"]

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            self.attack_types = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorDamageTypes.json")) as f:
            self.damage_types = json.load(f)

        self.permitted_attacks = self.attack_types[:3]

    def take_damage(self, damage, damage_type):
        # damage the player takes
        try:
            dmg = damage - \
                math.ceil(self.stats[damage_type["armor_type_that_absorbs"]])
        except KeyError:
            dmg = damage

            # check if the damage is blocked
        roll = random.randint(0, 100)
        if self.stats["Block Chance"] > roll or dmg <= 0:
            return self.information["block_damage_text"].format(self)

        self.stats["Health"] -= dmg
        if self.stats["Health"] <= 0:
            return self.die()
        # return info
        return self.information["take_damage_text"].format(self, dmg, self, self.stats['Health'])

    def damage_enemy(self, otherGladiator, damage_type_id=0):
        # roll to see if attack hit
        roll = random.randint(0, 100)
        if self.stats["Attack Chance"] < roll:
            return self.information["dodge_text"].format(otherGladiator)

        # roll for critical damage
        roll = random.randint(0, 100)

        dmg_type = None
        for i in self.damage_types:
            if i["damage_type_id"] == damage_type_id:
                dmg_type = i
                break
        else:
            raise IndexError("Damage type id could not be found")

        min_dmg = self.stats[dmg_type["min_damage_stat"]]
        max_dmg = self.stats[dmg_type["max_damage_stat"]]

        # roll for damage
        dmg = math.ceil(random.randint(min_dmg, max_dmg))
        if self.stats["Critical Damage Chance"] > roll:
            crit_dmg = math.ceil(dmg * self.stats["Critical Damage Boost"])
            return self.information["critical_hit_text"] + otherGladiator.take_damage(crit_dmg, dmg_type)
        else:
            return otherGladiator.take_damage(dmg, dmg_type)

    def attack(self, otherGladiator, attack_type_id=0, damage_type_id=0):
        if not isinstance(otherGladiator, GladiatorPlayer):
            raise ValueError(
                "otherGladiator must be an instance of GladiatorPlayer")

        # find the attack corresponding the id
        attack = None
        for atk in self.permitted_attacks:
            if atk["id"] == attack_type_id:
                attack = atk
                break
        else:
            raise IndexError("Attack type id could not been found")

        self.buff(attack["buffs"])
        inf = self.damage_enemy(otherGladiator, attack["damage_type_id"])
        self.buff(attack["buffs"], buff_type="debuff")
        return inf

    def die(self):
        self.dead = True
        return random.choice(self.information["death_texts"]).format(self)

    def equip_sword(self, sword: GladiatorSword):
        if not self.sword_equipped:
            self.stats += sword
            self.sword_equipped = sword

    def equip_armor(self, armor: GladiatorArmor):
        if not self.armor_equipped:
            self.stats += armor
            self.armor_equipped = armor

    def remove_sword(self):
        if self.sword_equipped:
            self.sword_equipped = None

    def remove_armor(self):
        if self.armor_equipped:
            self.armor_equipped = None

    def buff(self, buff: GladiatorBuff, buff_type="buff"):
        if buff_type == "buff":
            self.stats += buff
        elif buff_type == "debuff":
            self.stats -= buff
            if self.stats["Health"] <= 0:
                self.die()

    def unlock_attack_type(self, attack_type_id):
        for i in self.permitted_attacks:
            if i["id"] == attack_type_id:
                return
        self.permitted_attacks.append(self.attack_types[attack_type_id])

    def __repr__(self):
        return f"<@{self.id}>"
