import json
import os

class TypeData:
    _instance = None
    move_types = {}
    type_effectiveness = {}

    @classmethod
    def load_data(cls):
        """Loads the move types and type effectiveness data into the class."""
        if cls._instance is None:
            cls._instance = cls()
            data_path = os.path.join(os.path.dirname(__file__), "../data")
            with open(os.path.join(data_path, "move_types.json"), "r") as mt_file:
                cls.move_types = json.load(mt_file)
            with open(os.path.join(data_path, "type_effectiveness.json"), "r") as te_file:
                cls.type_effectiveness = json.load(te_file)

    @classmethod
    def get_move_type(cls, move):
        """Returns the type of the given move."""
        return cls.move_types.get(move, None)

    @classmethod
    def calculate_effectiveness(cls, attacking_type, defending_types):
        """Calculates the effectiveness of an attack against defending types."""
        multiplier = 1.0
        for defending_type in defending_types:
            multiplier *= cls.type_effectiveness.get(attacking_type, {}).get(defending_type, 1.0)
        return multiplier
