import random
import math
from Gladiator.GladiatorStats import GladiatorStats
import json
import os

INITIAL_ATTACK_TYPES_COUNT = 3


class GladiatorPlayer:
    def __init__(self, member):
        self.Member = member
        self.id = self.Member.id
        self.dead = False
        #self.id = 1
        with open(os.path.join("Gladiator", "GladiatorStats.json")) as f:
            self.stats = GladiatorStats(json.load(f)["Gladiator_initial_stats"])

        with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
            self.information = json.load(f)["game_information_texts"]

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorAttackBuffs.json")) as f:
            self.attack_types = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorDamageTypes.json")) as f:
            self.damage_types = json.load(f)

        with open(os.path.join("Gladiator", "Equipments", "GladiatorEquipments.json")) as f:
            self.equipments = json.load(f)

        with open(os.path.join("Gladiator", "AttackInformation", "GladiatorTurnDebuffs.json")) as f:
            self.turn_debuffs = json.load(f)

        with open(os.path.join("Gladiator", "Equipments", "GladiatorSlots.json")) as f:
            self.equipment_slots = json.load(f)

        self.permitted_attacks = self.attack_types[:INITIAL_ATTACK_TYPES_COUNT]
        self.debuffs = []

    def take_damage(self, damage, damage_type):
        try:
            dmg = damage - self.stats[damage_type["armor_type_that_absorbs"]]
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
        inf = ""
        # roll to see if attack hit
        roll = random.randint(0, 100)
        if self.stats["Attack Chance"] < roll:
            return self.information["dodge_text"].format(otherGladiator)

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
        dmg = random.randint(min_dmg, max_dmg)

        # roll for critical damage
        crit_roll = random.randint(0, 100)
        try:
            if self.stats["Debuff Chance"] > 0:
                # roll for debuff effect to other player
                if self.stats["Debuff Chance"] > random.randint(0, 100):
                    inf += otherGladiator.take_debuff(
                        self.stats["debuff_id"])
        except KeyError:
            pass

        if self.stats["Critical Damage Chance"] > crit_roll:
            crit_dmg = math.ceil(dmg * self.stats["Critical Damage Boost"])
            return inf + self.information["critical_hit_text"] + otherGladiator.take_damage(crit_dmg, dmg_type)
        else:
            return inf + otherGladiator.take_damage(dmg, dmg_type)

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

    def equip_item(self, equipment_id, equipment_slot_id):
        slot = None
        # search for the slot
        for k in self.equipment_slots:
            if k["id"] == equipment_slot_id:
                slot = k
                break
        else:
            raise IndexError("Equipment Slot couldnt be found.")

        # if there is an equipment equipped already in the slot,
        # do nothing, and return
        if slot["Equipment"]:
            return
        else:
            for equipment in self.equipments:
                if equipment["id"] == equipment_id and equipment["equipment_slot_id"] == equipment_slot_id:
                    slot["Equipment"] = equipment
                    self.stats += equipment["buffs"]
                    if equipment["debuff_id"] != -1:
                        for turn_dbf in self.turn_debuffs:
                            if turn_dbf["debuff_stats"]["debuff_id"] == equipment["debuff_id"]:
                                self.stats += turn_dbf["debuff_stats"]
                                break
                        else:
                            raise IndexError("Turn debuff id couldnt be found")
                    break
            else:
                raise IndexError("Equipment couldnt be found.")

    def buff(self, buff: GladiatorStats, buff_type="buff"):
        if buff_type == "buff":
            self.stats += buff
        elif buff_type == "debuff":
            self.stats -= buff

    def take_debuff(self, turn_debuff_id):
        # find the corresponding debuff in the json file
        debuff = None
        for k in self.turn_debuffs:
            if k["debuff_stats"]["debuff_id"] == turn_debuff_id:
                debuff = k
                break
        else:
            raise IndexError("Turn Debuff couldnt be found")

        # if the given debuff is already affecting the player,
        # make it last more turns
        for dbf in self.debuffs:
            if dbf["debuff_stats"]["debuff_id"] == debuff["debuff_stats"]["debuff_id"]:
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
                else:
                    del self.debuffs[index]

            return inf

    def unlock_attack_type(self, attack_type_id):
        for i in self.permitted_attacks:
            if i["id"] == attack_type_id:
                return
        self.permitted_attacks.append(self.attack_types[attack_type_id])

    def __repr__(self):
        return f"<@{self.id}>"
