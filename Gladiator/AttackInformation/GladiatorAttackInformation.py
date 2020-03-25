import json
import os

class GladiatorAttackInformation:
    def __init__(self):
        self.attack_types = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GladiatorAttackBuffs.json"), "r"))
        self.damage_types =  json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GladiatorDamageTypes.json"), "r"))
        self.turn_debuffs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GladiatorTurnDebuffs.json"), "r"))
    
    def find_attack_type(self, attack_type_id : int):
        # find the attack corresponding the id
        for atk in self.attack_types:
            if atk["id"] == attack_type_id:
                return atk
        return None

    def find_damage_type(self, damage_type_id : int):
        for i in self.damage_types:
            if i["damage_type_id"] == damage_type_id:
                return i
        return None

    def find_turn_debuff_id(self, turn_debuff_id : int):
        for turn_dbf in self.turn_debuffs:
            if turn_dbf["debuff_stats"]["debuff_id"] == turn_debuff_id:
                return turn_dbf
        return None
