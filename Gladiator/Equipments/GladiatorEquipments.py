import json
import os


class GladiatorEquipments:
    def __init__(self):
        self.equipments = json.load(open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "GladiatorEquipments.json"), "r"))
        self.slots = json.load(open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "GladiatorSlots.json"), "r"))

    def find_equipment(self, equipment_name: str = "") -> dict:
        for equipment in self.equipments:
            if equipment["name"] == equipment_name:
                return equipment
        return None

    def get_equipment_with_slot_name(self, equipment_name: str ="", slot_name: str="") -> dict:
        for equipment in self.equipments:
            if equipment["type"] == slot_name and equipment["name"] == equipment_name:
                return equipment
        return None

    def find_slot(self, slot_name: str = "") -> dict:
        for slot in self.slots:
            if slot["Slot Name"] == slot_name:
                return slot
        return None

    def update_slot(self, slot_name: str, equipment=None) -> None:
        slot = self.find_slot(slot_name)
        slot["Equipment"] = equipment

    def get_all_slots(self):
        return self.slots

    def get_all_equipments_from_slot_name(self, slot_name: str) -> list:
        equipments = []
        for equipment in self.equipments:
            if equipment["type"] == slot_name:
                equipments.append(equipment)
        return equipments

    def get_all_equipments(self):
        return self.equipments

    def get_equipment_name_by_emoji(self, emoji, slot_name: str) -> str:
        for eq in self.equipments:
            if eq["reaction_emoji"] == emoji and eq["type"] == slot_name:
                return eq["name"]
        return None
