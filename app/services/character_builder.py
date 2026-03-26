from typing import Dict, Any, List, Optional
from app.data.srd_loader import srd_loader

class CharacterBuilderService:
    def __init__(self):
        self.loader = srd_loader

    def validate_character_choices(self, class_name: str, race_name: str,
                                 background_name: str, equipment_names: List[str] = None,
                                 spell_names: List[str] = None) -> Dict[str, Any]:
        """
        Validates whether the chosen character elements exist in the SRD.
        Returns a dictionary indicating valid/invalid status for each.
        """
        equipment_names = equipment_names or []
        spell_names = spell_names or []

        result = {
            "is_valid": True,
            "errors": []
        }

        # Check Class
        cls = self.loader.get_class(class_name)
        if not cls:
            result["is_valid"] = False
            result["errors"].append(f"Class '{class_name}' not found.")

        # Check Race
        race = self.loader.get_race(race_name)
        if not race:
            result["is_valid"] = False
            result["errors"].append(f"Race '{race_name}' not found.")

        # Check Background
        bg = self.loader.get_background(background_name)
        if not bg:
            result["is_valid"] = False
            result["errors"].append(f"Background '{background_name}' not found.")

        # Check Equipment
        invalid_equipment = []
        for eq_name in equipment_names:
            eq = self.loader.get_equipment(eq_name)
            if not eq:
                invalid_equipment.append(eq_name)

        if invalid_equipment:
            result["is_valid"] = False
            result["errors"].append(f"Equipment not found: {', '.join(invalid_equipment)}")

        # Check Spells
        invalid_spells = []
        for spell_name in spell_names:
            spell = self.loader.get_spell_by_name(spell_name)
            if not spell:
                invalid_spells.append(spell_name)

        if invalid_spells:
            result["is_valid"] = False
            result["errors"].append(f"Spells not found: {', '.join(invalid_spells)}")

        return result

    def calculate_hp(self, class_name: str, constitution_modifier: int) -> int:
        """Calculates starting hit points based on class hit die + Con mod."""
        cls = self.loader.get_class(class_name)
        if not cls:
            raise ValueError(f"Unknown class '{class_name}'")

        hit_die = cls.get("hit_die", 0)
        return hit_die + constitution_modifier

    def calculate_ac(self, equipment_names: List[str], dexterity_modifier: int) -> int:
        """
        Calculates Armor Class based on equipped armor and dex modifier.
        This is a basic implementation assuming 'armor' objects have an 'armor_class' field
        with 'base' and 'dex_bonus' (True/False) keys in the SRD structure.
        """
        base_ac = 10
        dex_bonus_allowed = True
        max_dex_bonus = 100 # Effectively unlimited
        shield_bonus = 0

        has_armor = False

        for eq_name in equipment_names:
            eq = self.loader.get_equipment(eq_name)
            if not eq:
                continue

            # If it's armor
            if eq.get("equipment_category", {}).get("name") == "Armor":
                armor_cat = eq.get("armor_category", "")
                ac_info = eq.get("armor_class", {})

                if armor_cat == "Shield":
                    shield_bonus += ac_info.get("base", 2)
                else:
                    has_armor = True
                    base_ac = ac_info.get("base", 10)
                    dex_bonus_allowed = ac_info.get("dex_bonus", False)
                    max_dex_bonus = ac_info.get("max_bonus", 100) if ac_info.get("max_bonus") is not None else 100

        # Calculate final AC
        total_ac = base_ac + shield_bonus

        if dex_bonus_allowed:
            applicable_dex = dexterity_modifier
            if applicable_dex > max_dex_bonus:
                applicable_dex = max_dex_bonus
            total_ac += applicable_dex

        return total_ac

    def get_proficiencies(self, class_name: str, race_name: str, background_name: str) -> List[Dict[str, Any]]:
        """
        Aggregates base proficiencies from class, race, and background.
        (Note: ignores proficiency *choices*, returns only fixed base proficiencies)
        """
        proficiencies = []

        cls = self.loader.get_class(class_name)
        if cls and "proficiencies" in cls:
            for p in cls["proficiencies"]:
                if p not in proficiencies:
                    proficiencies.append(p)

        race = self.loader.get_race(race_name)
        if race and "starting_proficiencies" in race:
            for p in race["starting_proficiencies"]:
                if p not in proficiencies:
                    proficiencies.append(p)

        bg = self.loader.get_background(background_name)
        if bg and "starting_proficiencies" in bg:
            for p in bg["starting_proficiencies"]:
                if p not in proficiencies:
                    proficiencies.append(p)

        return proficiencies

    def suggest_starting_equipment(self, class_name: str) -> List[Dict[str, Any]]:
        """Returns the starting equipment for the class."""
        cls = self.loader.get_class(class_name)
        if not cls:
            raise ValueError(f"Unknown class '{class_name}'")

        equipment = []

        # Add basic starting equipment
        if "starting_equipment" in cls:
            equipment.extend(cls["starting_equipment"])

        # Also return starting equipment options so the UI can present them
        if "starting_equipment_options" in cls:
            equipment.extend(cls["starting_equipment_options"])

        return equipment

character_builder = CharacterBuilderService()
