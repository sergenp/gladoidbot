import sys
import pymongo
import os
sys.path.append("..")

try:
    from MongoDB import mongo_settings
    CONNECTION_STRING = mongo_settings.CONNECTION_STRING
except ModuleNotFoundError:
    CONNECTION_STRING = os.environ["MongoDB_CONNECTION_STRING"]
    
class GladiatorGameInformation():
    def __init__(self):
        self.client = pymongo.MongoClient(CONNECTION_STRING).HutAssistant

    def save_profile(self, profile_dict: dict):
        self.client.UserProfiles.find_one_and_replace({'_id' : profile_dict['_id']}, profile_dict, upsert=True)

    def get_profile(self, profile_id: int) -> dict:
        return self.client.UserProfiles.find_one({'_id' : str(profile_id)})

    def get_attack_information(self) -> list:
        return self.client.AttackInformation.find()

    def get_npcs(self) -> list:
        return self.client.NPCs.find()

    def get_gladiator_game_settings(self) -> dict:
        return self.client.GameSettings.find_one()

    def get_npc_events(self) -> list:
        return self.client.NPCEvents.find()

    def get_get_duel_events(self) -> list:
        return self.client.DuelEvents.find()

    def get_equipments(self) -> list:
        return self.client.Equipments.find()

    def get_equipment_slots(self) -> list:
        return self.client.EquipmentSlots.find()
