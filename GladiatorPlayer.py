import random
import math
from GladiatorStats import GladiatorStats, GladiatorArmor, GladiatorSword, GladiatorBuff
from enum import Enum


class AttackTypes(Enum):
    Thrust = 1
    Slash = 2
    Defensive = 3
    Flurry = 4


class GladiatorPlayer:
    def __init__(self, member):
        self.Member = member
        self.id = self.Member.id
        self.stats = GladiatorStats()
        self.sword_equipped = None
        self.armor_equipped = None
        self.dead = False

    def take_damage(self, damage):
        # check if the damage is blocked
        roll = random.randint(0, 100)
        if self.stats["Block Chance"] > roll:
            return f"**{self} has blocked the damage**"
        # damage the player
        dmg = damage - math.ceil(self.stats["Armor"])
        if dmg < 0:
            dmg = 0
        self.stats["Health"] -= damage - math.ceil(self.stats["Armor"])
        if self.stats["Health"] <= 0:
            return self.die()
        # return info
        return f"{self} took **{damage - math.ceil(self.stats['Armor'])} damage**, {self} has **{self.stats['Health']} HP** remaining"

    def damageEnemy(self, otherGladiator):
        # roll to see if attack hit
        roll = random.randint(0, 100)
        if self.stats["Attack Chance"] < roll:
            return f"**{otherGladiator} has dodged your attack!**"

        # roll for critical damage
        roll = random.randint(0, 100)
        # roll for damage
        dmg = math.ceil(random.randint(
            self.stats["Attack Min. Damage"], self.stats["Attack Max. Damage"]))
        if self.stats["Critical Damage Chance"] > roll:
            crit_dmg = math.ceil(dmg * self.stats["Critical Damage Boost"])
            return "It is a **CRITICAL** hit " + otherGladiator.take_damage(crit_dmg)
        else:
            return otherGladiator.take_damage(dmg)

    def attack(self, otherGladiator, attack_type=AttackTypes.Thrust):
        if not isinstance(otherGladiator, GladiatorPlayer):
            raise ValueError(
                "otherGladiator must be an instance of GladiatorPlayer")
        thrustBuff = GladiatorBuff({"Attack Chance": 10})
        slashBuff = GladiatorBuff(
            {"Attack Chance": -10, "Attack Min. Damage": 1, "Attack Max. Damage": 1})
        defensiveBuff = GladiatorBuff(
            {"Critical Damage Chance": 30, "Critical Damage Boost": -0.2, "Attack Chance": -10})
        flurryBuff = GladiatorBuff(
            {"Attack Chance": -40, "Attack Min. Damage": 4, "Attack Max. Damage": 4, "Critical Damage Boost": 0.2})
        inf = ""
        if attack_type is AttackTypes.Thrust:
            self.buff(thrustBuff)
            inf = self.damageEnemy(otherGladiator)
            self.buff(thrustBuff, buff_type="debuff")

        elif attack_type is AttackTypes.Slash:
            self.buff(slashBuff)
            inf = self.damageEnemy(otherGladiator)
            self.buff(slashBuff, buff_type="debuff")

        elif attack_type is AttackTypes.Defensive:
            self.buff(defensiveBuff)
            inf = self.damageEnemy(otherGladiator)
            self.buff(defensiveBuff, buff_type="debuff")

        elif attack_type is AttackTypes.Flurry:
            self.buff(flurryBuff)
            inf = self.damageEnemy(otherGladiator)
            self.buff(flurryBuff, buff_type="debuff")

        return inf

    def die(self):
        self.dead = True
        return f"**{self} has died**"

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

    def __repr__(self):
        return f"<@{self.id}>"
