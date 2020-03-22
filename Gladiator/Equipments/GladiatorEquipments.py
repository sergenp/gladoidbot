import json
import os

class GladiatorEquipments:
    def __init__(self):
        self.equipments = json.load(open(os.path.join(os.path.dirname(__file__), "GladiatorEquipments.json"),"r"))
        self.slots = json.load(open(os.path.join(os.path.dirname(__file__), "GladiatorSlots.json"), "r"))

    def find_equipment(self, equipment_id : int):
        for equipment in self.equipments:
            if equipment["id"] == equipment_id:
                return equipment

    def find_slot(self, slot_id : int):
        for slot in self.slots:
            if slot["id"] == slot_id:
                return slot

    def update_slot(self, slot_id : int, equipment):
        self.slots[slot_id]["Equipment"] = equipment
