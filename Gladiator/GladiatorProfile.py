import json
import os
from Gladiator.Equipments.GladiatorEquipments import GladiatorEquipments
import math
import random


def save_profile(func):
    def wrapper(self, *args, **kwargs):
        out = func(self, *args, **kwargs)
        json.dump(self.profile_stats, open(os.path.join(os.path.dirname(__file__),
                                                        "UserProfileData", f"{self.profile_stats['Id']}.json"), "w"), indent=4, sort_keys=True)
        return out
    return wrapper


class GladiatorProfile():
    @save_profile
    def __init__(self, member, **kwargs):
        self.equipment_info = GladiatorEquipments()
        self.member = member

        profile_settings = json.load(open(os.path.join(os.path.dirname(
            __file__), "Settings", "GladiatorGameSettings.json"), "r"))["profile_settings"]
        self.XP_TO_LEVEL_MULTIPLIER = profile_settings["XP_TO_LEVEL_MULTIPLIER"]
        self.XP_TO_LEVEL_WHEN_LOST_MULTIPLIER = profile_settings["XP_TO_LEVEL_WHEN_LOST_MULTIPLIER"]
        self.XP_GAIN_MULTIPLIER = profile_settings["XP_GAIN_MULTIPLIER"]
        self.MAX_COIN_REWARD = profile_settings["MAX_COIN_REWARD"]
        self.MIN_COIN_REWARD = profile_settings["MIN_COIN_REWARD"]
        self.COIN_DECAY_CONSANT = profile_settings["COIN_DECAY_CONSTANT"]
        self.LEVEL_UP_DIFFICULTY_CONSTANT = profile_settings["LEVEL_UP_DIFFICULTY_CONSTANT"]

        if os.path.exists(os.path.join(os.path.dirname(__file__), "UserProfileData", f"{self.member.id}.json")):
            self.profile_stats = json.load(
                open(os.path.join(os.path.dirname(__file__), "UserProfileData", f"{self.member.id}.json"), "r"))
        else:
            self.profile_stats = json.load(
                open(os.path.join(os.path.dirname(__file__), "UserProfileData", "default_profile.json"), "r"))
            self.profile_stats["Id"] = self.profile_stats["Id"].format(
                self.member.id)

            # add default items for the people whomst have first created their profile
            self.profile_stats["Inventory"].append(
                self.equipment_info.find_equipment(0))  # Light Armor
            self.profile_stats["Inventory"].append(
                self.equipment_info.find_equipment(3))  # Spear

        for key in kwargs:
            self.profile_stats[key] = kwargs.get(key)

    @save_profile
    def buy_equipment(self, equipment_id: int):
        equipment = self.equipment_info.find_equipment(equipment_id)

        if not equipment:
            return "Couldn't find the equipment for given id"

        for eq in self.profile_stats["Inventory"]:
            if eq["id"] == equipment["id"]:
                return f"You are already using {eq['name']}!"

        if self.profile_stats["HutCoins"] - equipment["price"] < 0:
            return "You cannot afford this item!"

        self.profile_stats["HutCoins"] -= equipment["price"]

        slot = self.equipment_info.find_slot(
            equipment["equipment_slot_id"])
        # if there is a slot already occupied in the profile, remove that slot and that equipment
        for index, eq in enumerate(self.profile_stats["Inventory"]):
            if eq["equipment_slot_id"] == slot["id"]:
                del self.profile_stats["Inventory"][index]
                break
        # add the equipment to the profile inventory
        self.profile_stats["Inventory"].append(equipment)
        return f"Successfully bought **{equipment['name']}**. You have **{self.profile_stats['HutCoins']} HutCoins** left."

    @save_profile
    def update_games(self, other_profile_level: int, won=False):
        self.profile_stats["Games Played"] += 1
        if won:
            self.profile_stats["Games Won"] += 1
            return self.gain_xp(other_profile_level)
        else:
            self.profile_stats["Games Lost"] += 1
            return self.gain_xp(other_profile_level/self.XP_TO_LEVEL_WHEN_LOST_MULTIPLIER)

    @save_profile
    def add_coin(self, amount):
        self.profile_stats["HutCoins"] += amount
        return f"**You earned {amount} HutCoins!**"

    @save_profile
    def reward_player(self, other_profile_level: int):
        lvl_diff = self.get_level() - other_profile_level
        return self.add_coin(math.ceil((self.MAX_COIN_REWARD-self.MIN_COIN_REWARD + 1) *
                                       (math.exp(-self.COIN_DECAY_CONSANT*lvl_diff)) + self.MIN_COIN_REWARD - 1))

    def calculate_xp_for_next_level(self):
        return self.XP_TO_LEVEL_MULTIPLIER*(self.get_level()**2)*self.LEVEL_UP_DIFFICULTY_CONSTANT - (self.XP_TO_LEVEL_MULTIPLIER * self.get_level()) + 300

    @save_profile
    def gain_xp(self, other_profile_level: int):
        msg = ""
        xp_gained = math.ceil(other_profile_level /
                              self.get_level()) * self.XP_GAIN_MULTIPLIER

        xp_gained += random.randint(self.get_level(), self.get_level()*5)
        self.profile_stats["XP"] += xp_gained
        msg += f"Gained {xp_gained} XP\n"
        xp_for_next_level = self.calculate_xp_for_next_level()
        while self.profile_stats["XP"] > xp_for_next_level:
            self.profile_stats["Level"] += 1
            xp_for_next_level = self.calculate_xp_for_next_level()
            msg += f"You have levelled up!\n"
        
        self.profile_stats["XP To Next Level"] = self.calculate_xp_for_next_level()
        return msg

    def get_level(self):
        return self.profile_stats["Level"]

    @save_profile
    def event_bonus(self, profile_stat_key: str, amount: int):
        self.profile_stats[profile_stat_key] += amount
        return f"Added {amount} of {profile_stat_key} to your profile!"

    def __repr__(self):        
        msg = ""
        for key in self.profile_stats.keys():
            if not key in ("Id", "armor_id", "weapon_id", "boosts"):
                if key == "Inventory":
                    for item in self.profile_stats[key]:
                        msg += f"{item['type']} : **{item['name']}\n**"
                    continue
                msg += f"{key} : **{self.profile_stats[key]}**\n"
        return msg
