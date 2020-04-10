import sys
import random
import math
import os
import json

sys.path.append('..')
from Gladiator.Equipments.GladiatorEquipments import GladiatorEquipments
from MongoDB.Connector import Connector

MongoDatabase = Connector()

def save_profile(func):
    def wrapper(self, *args, **kwargs):
        out = func(self, *args, **kwargs)
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "UserProfileData", f"{self.profile_stats['_id']}.json")
        json.dump(self.profile_stats, open(
            filename, "w"), indent=4, sort_keys=True)
        MongoDatabase.save_profile(self.profile_stats)
        return out
    return wrapper


class Profile():
    def __init__(self, member, **kwargs):
        self.member = member
        profile_path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), "UserProfileData", f"{self.member.id}.json")
       
        profile_settings = json.load(open(os.path.join(os.path.dirname(
            __file__), "Settings", "GladiatorGameSettings.json"), "r"))["profile_settings"]
        self.XP_TO_LEVEL_MULTIPLIER = profile_settings["XP_TO_LEVEL_MULTIPLIER"]
        self.XP_TO_LEVEL_WHEN_LOST_MULTIPLIER = profile_settings["XP_TO_LEVEL_WHEN_LOST_MULTIPLIER"]
        self.XP_GAIN_MULTIPLIER = profile_settings["XP_GAIN_MULTIPLIER"]
        self.LEVEL_UP_DIFFICULTY_CONSTANT = profile_settings["LEVEL_UP_DIFFICULTY_CONSTANT"]
        self.LEVEL_UP_START_POINT = profile_settings["LEVEL_UP_START_POINT"]
        if os.path.exists(profile_path):
            self.profile_stats = json.load(open(profile_path, "r"))
        else:
            self.create_default_profile(**kwargs)

    @save_profile
    def create_default_profile(self, **kwargs):
        self.profile_stats = json.load(
            open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "UserProfileData", "default_profile.json"), "r"))
        self.profile_stats["_id"] = self.member.id
        self.profile_stats.update(kwargs)

    def get_level(self):
        return self.profile_stats["Level"]

    @save_profile
    def event_bonus(self, profile_stat_key: str, amount: int) -> str:
        self.profile_stats[profile_stat_key] += amount
        return f"Added **{amount} {profile_stat_key}** to your profile!"
 
    def calculate_xp_for_next_level(self):
        return round(self.XP_TO_LEVEL_MULTIPLIER*(self.get_level()**2)*self.LEVEL_UP_DIFFICULTY_CONSTANT - (self.XP_TO_LEVEL_MULTIPLIER * self.get_level()) + self.LEVEL_UP_START_POINT) + 1

class GladiatorProfile(Profile):
    def __init__(self, member, **kwargs):
        super().__init__(member=member)
        self.equipment_info = GladiatorEquipments()

    @save_profile
    def buy_equipment(self, equipment_name: str) -> str:
        equipment = self.equipment_info.find_equipment(equipment_name)

        if not equipment:
            return "Couldn't find the equipment for given id"

        for eq in self.profile_stats["Inventory"]:
            if eq["name"] == equipment["name"]:
                return f"You are already using {eq['name']}!"

        if self.profile_stats["HutCoins"] - equipment["price"] < 0:
            return "You cannot afford this item!"

        self.profile_stats["HutCoins"] -= equipment["price"]

        slot = self.equipment_info.find_slot(
            equipment["type"])
        # if there is a slot already occupied in the profile, remove that slot and that equipment
        for index, eq in enumerate(self.profile_stats["Inventory"]):
            if eq["type"] == slot["Slot Name"]:
                del self.profile_stats["Inventory"][index]
                break
        # add the equipment to the profile inventory
        self.profile_stats["Inventory"].append({"name" : equipment["name"], "type" : equipment["type"]})
        return f"Successfully bought **{equipment['name']}**. You have **{self.profile_stats['HutCoins']} HutCoins** left."

    def update_games(self, other_profile_level: int, won: bool, **kwargs) -> str:
        self.profile_stats["Games Played"] += 1
        if won:
            self.profile_stats["Games Won"] += 1
            return self.gain_xp(other_profile_level, kwargs.get("XP", 0)) + self.reward_player(kwargs.get("HutCoins", 0))
       
        self.profile_stats["Games Lost"] += 1
        return self.gain_xp(other_profile_level/self.XP_TO_LEVEL_WHEN_LOST_MULTIPLIER)

    @save_profile
    def reward_player(self, bonus_coins: int = 0) -> str:
        coin = random.randint(20, 75) + bonus_coins
        self.profile_stats["HutCoins"] += coin
        return f"**You earned {coin} HutCoins!**"

    @save_profile
    def gain_xp(self, other_profile_level: int, bonus_xp: int = 0) -> str:
        xp_gained = math.ceil(other_profile_level /
                              self.get_level()) * self.XP_GAIN_MULTIPLIER + random.randint(self.get_level(), self.get_level()*5) + bonus_xp

        self.profile_stats["XP"] += xp_gained
        msg = f"Gained {xp_gained} XP\n"
        xp_for_next_level = self.calculate_xp_for_next_level()
        while self.profile_stats["XP"] >= xp_for_next_level:
            self.profile_stats["Level"] += 1
            xp_for_next_level = self.calculate_xp_for_next_level()
            msg += f"You have levelled up!\n"

        self.profile_stats["XP To Next Level"] = xp_for_next_level
        return msg

    def get_stats(self):
        return self.profile_stats["Stats"]

    def __repr__(self):
        msg = ""
        for key in self.profile_stats.keys():
            if not key in ("_id", "Stats"):
                if key == "Inventory":
                    for item in self.profile_stats[key]:
                        msg += f"{item['type']} : **{item['name']}\n**"
                    continue
                msg += f"{key} : **{self.profile_stats[key]}**\n"
        return msg
