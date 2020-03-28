import json
import os


class GladiatorEquipments:
    def __init__(self):
        self.equipments = json.load(open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "GladiatorEquipments.json"), "r"))
        self.slots = json.load(open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "GladiatorSlots.json"), "r"))

    def find_equipment(self, equipment_id: int):
        for equipment in self.equipments:
            if equipment["id"] == equipment_id:
                return equipment
        return None

    def get_equipment_with_slot_id(self, equipment_id: int, slot_id: int):
        for equipment in self.equipments:
            if equipment["equipment_slot_id"] == slot_id and equipment["id"] == equipment_id:
                return equipment
        return None

    def find_slot(self, slot_id: int):
        for slot in self.slots:
            if slot["id"] == slot_id:
                return slot
        return None

    def update_slot(self, slot_id: int, equipment):
        slot = self.find_slot(slot_id)
        slot["Equipment"] = equipment

    def get_all_slots(self):
        return self.slots

    def get_all_equipments_from_slot_id(self, slot_id: int):
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
        return None
