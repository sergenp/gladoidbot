import os
import glob
import json

class NPCFinder:
    def __init__(self):
        self.npcs = []
        for npc_path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*.json")):
            self.npcs.append(npc_path)

    def get_npc_by_id(self, npc_id : int) -> str:
        '''
            return NPC file path given npc_id
        '''
        for npc in self.npcs:
            with open(npc) as f:
                if json.load(f)["id"] == npc_id:
                    return npc
        return None
