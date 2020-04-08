import json
import os

class GladiatorAttackInformation:
    def __init__(self):
        self.attack_types = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GladiatorAttackBuffs.json"), "r"))
        self.damage_types = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GladiatorDamageTypes.json"), "r"))
        self.turn_debuffs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GladiatorTurnDebuffs.json"), "r"))
    
    def find_attack_type(self, attack_name: str):
        # find the attack corresponding the id
        for atk in self.attack_types:
            if atk["name"] == attack_name:
                return atk
        return None

    def find_damage_type(self, damage_type_name: str):
        for i in self.damage_types:
            if i["damage_type_name"] == damage_type_name:
                return i
        return None

    def find_turn_debuff(self, turn_debuff_name: str):
        for turn_dbf in self.turn_debuffs:
            if turn_dbf["debuff_stats"]["Debuff Type"] == turn_debuff_name:
                return turn_dbf
        return None
