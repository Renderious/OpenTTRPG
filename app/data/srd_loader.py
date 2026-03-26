import json
import os
from typing import Dict, List, Any, Optional

class SRDLoader:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            # Default to repo_root/data by going up two directories from app/data/srd_loader.py
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
        else:
            self.data_dir = data_dir
        self.classes: List[Dict[str, Any]] = []
        self.races: List[Dict[str, Any]] = []
        self.backgrounds: List[Dict[str, Any]] = []
        self.spells: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        self.conditions: List[Dict[str, Any]] = []

        # Load all data on init
        self._load_data()
        self._validate_data()

    def _load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing required SRD data file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"SRD data file {filename} must contain a list of objects")

        return data

    def _load_data(self) -> None:
        self.classes = self._load_json_file("classes.json")
        self.races = self._load_json_file("races.json")
        self.backgrounds = self._load_json_file("backgrounds.json")
        self.spells = self._load_json_file("spells.json")
        self.equipment = self._load_json_file("equipment.json")
        self.conditions = self._load_json_file("conditions.json")

    def _validate_data(self) -> None:
        """Validates that loaded data has elements."""
        if not self.classes:
            raise ValueError("No classes loaded from SRD data.")
        if not self.races:
            raise ValueError("No races loaded from SRD data.")
        if not self.backgrounds:
            raise ValueError("No backgrounds loaded from SRD data.")
        if not self.spells:
            raise ValueError("No spells loaded from SRD data.")
        if not self.equipment:
            raise ValueError("No equipment loaded from SRD data.")
        if not self.conditions:
            raise ValueError("No conditions loaded from SRD data.")

    def _find_by_name(self, collection: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
        name_lower = name.lower()
        for item in collection:
            if item.get("name", "").lower() == name_lower:
                return item
        return None

    def get_class(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_by_name(self.classes, name)

    def get_race(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_by_name(self.races, name)

    def get_background(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_by_name(self.backgrounds, name)

    def get_spell_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_by_name(self.spells, name)

    def get_equipment(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_by_name(self.equipment, name)

    def get_condition(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_by_name(self.conditions, name)

    def get_class_features(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Returns the class definition which includes its features/proficiencies."""
        return self.get_class(class_name)

# Global instance
srd_loader = SRDLoader()
