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
    
    def get_all_slots(self):
        return self.slots
    
    def get_all_equipments_from_slot_id(self, slot_id : int):
        equipments = []
        for equipment in self.equipments:
            if equipment["equipment_slot_id"] == slot_id:
                equipments.append(equipment)
        return equipments

    def get_all_equipments(self):
        return self.equipments

    def get_equipment_id_by_emoji(self, emoji, slot_id):
        for eq in self.equipments:
            if eq["reaction_emoji"] == emoji and eq["equipment_slot_id"] == slot_id:
                return eq["id"]


        
