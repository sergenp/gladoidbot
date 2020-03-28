import sys
sys.path.append('..')

import json
import os

from Gladiator.Player import Player
from Gladiator.AttackInformation.GladiatorAttackInformation import GladiatorAttackInformation

class GladiatorNPC(Player):
    def __init__(self, name, stats_path, **kwargs):
        super().__init__(stats_path)
        self.name = name
        self.stats += kwargs
        self.attack_information = GladiatorAttackInformation()
    
    def __repr__(self):
        return f"{self.name}"

a = GladiatorNPC("rat", os.path.join(os.path.dirname(os.path.abspath(__file__)), "NPCs", "Rat.json"))
b = GladiatorNPC("fat", os.path.join(os.path.dirname(os.path.abspath(__file__)), "NPCs", "Spider.json"))

print(a.stats)
print(b.stats)