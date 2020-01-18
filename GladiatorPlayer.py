import random
import math
from GladiatorStats import GladiatorStats, GladiatorArmor


class GladiatorPlayer:
    def __init__(self, name):
        self.name = name
        self.health = 30
        self.stats = GladiatorStats()

    def take_damage(self, damage):
        # check if the damage is blocked
        roll = random.randint(0, 100)
        if self.stats["block_chance"] > roll:
            return "Damage has been blocked"
        # damage the player
        self.health -= damage - math.ceil(self.stats["armor"])
        if self.health < 0:
            return self.die()
        # return info
        return f"{self.name}, total damage taken {damage - math.ceil(self.stats['armor'])} health remaining {self.health}"

    def attack(self, otherGladiator):
        if not isinstance(otherGladiator, GladiatorPlayer):
            raise ValueError(
                "otherGladiator must be instance of GladiatorPlayer")

        # roll to see if attack hit
        roll = random.randint(0, 100)
        if self.stats["attack_chance"] < roll:
            return f"{self.name}'s attack missed!"
        # roll for critical damage
        roll = random.randint(0, 100)
        if self.stats["crit_chance"] > roll:
            crit_dmg = math.ceil(self.stats["attack_damage"] *
                                 self.stats["crit_damage_boost"])
            return "It is a CRITICAL hit " + otherGladiator.take_damage(crit_dmg)
        else:
            return otherGladiator.take_damage(
                math.ceil(self.stats["attack_damage"]))

    def die(self):
        return "You have been defeated"

    def equip_sword(self, sword):
        self.stats += sword.stats

    def equip_armor(self, armor):
        self.stats += armor.stats
