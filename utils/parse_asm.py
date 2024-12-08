from typing import List
import os
import re
from pykmn.data.gen1 import MOVES, SPECIES
import json
import sys

sys.path.append("..")
from models.pokemon import Pokemon, Trainer, TrainerClass, serialize_trainerclasses


def parse_dex_data(data: str):
    """
    Parse the Pokémon data into a dictionary where the key is the Pokémon name (capitalized)
    and the value is the corresponding index number.

    Args:
        data (str): The string containing the Pokémon data.

    Returns:
        dict: A dictionary with Pokémon names as keys and their corresponding indices as values.
    """
    pokemon_dict = {}
    lines = data.strip().splitlines()

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("const"):
            # Split the line into the name and the value
            parts = stripped_line.split(";")
            name = (
                parts[0].split()[-1].strip().upper().replace("DEX_", "")
            )  # Extract and capitalize the name
            index = int(parts[1].strip())
            pokemon_dict[name] = index

    return pokemon_dict


def parse_move_choices(data: str):
    """
    Parse the move choices into a dictionary where the key is the trainer class
    and the value is a tuple of battle modifiers.

    Args:
        data (str): The string containing the move choices.

    Returns:
        dict: A dictionary with trainer classes as keys and a tuple of battle modifiers as values.
    """
    move_choices_dict = {}
    lines = data.strip().splitlines()

    for line in lines:
        # Split the line into the modifiers and the trainer class
        parts = line.split(";")
        modifiers = parts[0].replace("move_choices", "").strip()  # Extract modifiers
        trainer_class = parts[1].strip()  # Extract trainer class

        # Convert modifiers into a tuple of integers, or an empty tuple if no modifiers are present
        if modifiers:
            modifiers_tuple = tuple(map(int, modifiers.split(",")))
        else:
            modifiers_tuple = ()

        move_choices_dict[trainer_class] = modifiers_tuple

    return move_choices_dict


def parse_trainer_data(data: str, set_level: None | int) -> List[TrainerClass]:
    trainer_classes = []
    current_trainer_class = None
    current_location = None
    location_suffix_counts = {}  # Track suffix counts for each location

    for line in data.splitlines():
        line = line.strip()

        # Check for trainer class (e.g., Green3Data:)
        if line.endswith(":") and not line.startswith(";"):
            if current_trainer_class:
                trainer_classes.append(current_trainer_class)
            trainer_name = line[:-1]
            trainer_display_name = (
                trainer_name.replace("Data", "")
                if trainer_name.endswith("Data")
                else trainer_name
            )
            current_trainer_class = TrainerClass(name=trainer_display_name, trainers=[])
            current_location = None  # Reset location for new trainer class
            location_suffix_counts = {}  # Reset suffix counts for new trainer class

        # Check for location comments (e.g., ; Route 22)
        elif line.startswith(";"):
            current_location = line[1:].strip()

        # Check for Pokémon data (e.g., db $FF, 61, PIDGEOT, ...)
        elif line.startswith("db") and current_trainer_class:
            raw_data = line.split(" ", 1)[1].replace(" ", "").split(",")
            pokemon_team = []

            if raw_data[0] != "$FF":  # Case 1: First byte != $FF
                level = (
                    int(raw_data[0], 16)
                    if raw_data[0].startswith("$")
                    else int(raw_data[0])
                )
                for species in raw_data[1:]:
                    if species == "0":  # Null terminator
                        break
                    pokemon_team.append(
                        Pokemon(extra={"level": level if set_level is None else set_level}, species=species.capitalize())
                    )
            else:  # Case 2: First byte == $FF
                for i in range(1, len(raw_data) - 1, 2):
                    if raw_data[i] == "0":  # Null terminator
                        break
                    level = (
                        int(raw_data[i], 16)
                        if raw_data[i].startswith("$")
                        else int(raw_data[i])
                    )
                    species = raw_data[i + 1].capitalize()
                    pokemon_team.append(
                        Pokemon(extra={"level": level}, species=species)
                    )

            # Handle location suffix to avoid duplication
            location_name = (
                current_location if current_location else current_trainer_class.name
            )
            if location_name in location_suffix_counts:
                location_suffix_counts[location_name] += 1
                suffix = chr(
                    65 + location_suffix_counts[location_name] - 1
                )  # 'A', 'B', 'C', ...
                location_name = f"{location_name}-{suffix}"
            else:
                location_suffix_counts[location_name] = 1
                location_name = f"{location_name}-A"

            current_trainer_class.trainers.append(
                Trainer(
                    name=trainer_display_name,
                    location=location_name,
                    pokemon=pokemon_team,
                )
            )

    # Append the last trainer class
    if current_trainer_class:
        trainer_classes.append(current_trainer_class)

    return trainer_classes


def parse_learnset_moves(data: str) -> dict:
    """
    Parses Pokémon learnsets from the given data string.

    Args:
        data (str): Multiline string containing Pokémon data.

    Returns:
        dict: A dictionary where keys are Pokémon names and values are lists of tuples (level, move).
    """
    pokemon_moves = {}
    current_pokemon = None
    parsing_learnset = False

    for line in data.splitlines():
        line = line.strip()

        # Check for Pokémon name (e.g., MagnemiteEvosMoves:)
        if line.endswith("EvosMoves:"):
            current_pokemon = line.replace("EvosMoves:", "").strip()
            pokemon_moves[current_pokemon] = []
            parsing_learnset = False  # Reset learnset parsing for the new Pokémon

        # Check for the start of the learnset
        elif line.startswith("; Learnset"):
            parsing_learnset = True

        # Parse moves if in the learnset section
        elif parsing_learnset and line.startswith("db") and current_pokemon:
            raw_data = line.split(" ", 1)[1].split(",")
            for i in range(0, len(raw_data) - 1, 2):  # Process pairs of level and move
                level = raw_data[i].strip()
                move = raw_data[i + 1].strip()

                # End of learnset indicated by level `0`
                if level == "0":
                    parsing_learnset = False
                    break

                # Exclude "NO_MOVE" and convert level to int if numeric
                if move != "NO_MOVE":
                    level = int(level) if level.isdigit() else level
                    pokemon_moves[current_pokemon].append((level, move))

    return pokemon_moves


def get_pokemon_name_from_sprite_line(line: str) -> str:
    """
    Extracts the Pokémon name from a sprite line like 'dw NidoranFPicFront, NidoranFPicBack'.

    Args:
        line (str): Line containing sprite reference.

    Returns:
        str: Corrected Pokémon name without the 'PicFront' or 'PicBack' suffix.
    """
    match = re.search(r"dw (\w+)PicFront,", line)
    if match:
        return match.group(1)
    match = re.search(r"dw (\w+)PicBack,", line)
    if match:
        return match.group(1)
    return None  # If no match is found, return None.


def parse_level1_moves(base_stats_folder: str) -> dict:
    """
    Parses level 1 moves from Pokémon base stats files.

    Args:
        base_stats_folder (str): Path to the folder containing base stats files.

    Returns:
        dict: A dictionary where keys are Pokémon names and values are lists of level 1 moves.
    """
    level1_moves = {}

    # Iterate through all files in the folder
    for filename in os.listdir(base_stats_folder):
        if filename.endswith(".asm"):
            filepath = os.path.join(base_stats_folder, filename)
            with open(filepath, "r") as file:
                lines = file.readlines()
                current_pokemon = None  # This will hold the current Pokémon name

                for line in lines:
                    line = line.strip()

                    # Extract Pokémon name from sprite line (e.g., dw NidoranFPicFront, NidoranFPicBack)
                    pokemon_name = get_pokemon_name_from_sprite_line(line)
                    if pokemon_name is not None:
                        current_pokemon = (
                            pokemon_name  # Update the current Pokémon name
                        )

                    # Skip empty lines or comments
                    if not line or line.startswith(";"):
                        continue

                    # Look for the level 1 learnset part (level 1 moves usually after a comment or db 0)
                    if "level 1 learnset" in line:
                        # Extract moves from the line
                        moves_part = line.split("; level 1 learnset")[0].strip()
                        if moves_part.startswith("db"):
                            moves = re.findall(r"\b[A-Z_]+\b", moves_part)
                            moves = [move for move in moves if move != "NO_MOVE"]
                            if moves:
                                level1_moves[current_pokemon] = moves
                        break  # Stop after processing level 1 moves

    return level1_moves


def combine_moves(learnset_moves: dict, base_stats_moves: dict) -> dict:
    """
    Combines level 1 moves and level-up moves into a single dataset with level 1 moves first.

    Args:
        learnset_moves (dict): Parsed level-up moves.
        base_stats_moves (dict): Parsed level 1 moves.

    Returns:
        dict: Combined moves data for each Pokémon with level 1 moves first.
    """
    combined_moves = {}

    # First, add the level 1 moves
    for pokemon, moves in base_stats_moves.items():
        combined_moves[pokemon] = [(1, move) for move in moves]

    # Then, add the level-up moves
    for pokemon, moves in learnset_moves.items():
        if pokemon in combined_moves:
            combined_moves[pokemon].extend(moves)
        else:
            combined_moves[pokemon] = moves

    return combined_moves


def correct_pokemon_name(name: str) -> str:
    # Define the exceptions in a dictionary
    exceptions = {"Mr_mime": "MrMime", "Nidoran_f": "NidoranF", "Nidoran_m": "NidoranM"}

    # If the name is in the exceptions dictionary, return the corrected name
    if name in exceptions:
        return exceptions[name]

    # Otherwise, return the name with just the first letter capitalized and the rest in lowercase
    return name.capitalize()


def parse_moves(data: str):
    """
    Parse moves data from a string with a constant format and return a dictionary of moves.

    Args:
        data (str): The string containing the moves data.

    Returns:
        dict: A dictionary where each key is a move name, and the value is a dictionary
              containing 'power', 'accuracy', and 'type'.
    """
    moves = {}
    lines = data.strip().splitlines()

    for line in lines:
        if line.strip().startswith("move"):
            parts = line.split(",")
            name = parts[0].split()[1].strip()
            power = int(parts[2].strip())
            move_type = parts[3].strip()
            accuracy = int(parts[4].strip())

            moves[name] = {
                "power": power,
                "accuracy": accuracy,
                "type": move_type.replace("_TYPE", "").capitalize(),
            }

    return moves


def populate_trainer_moves(
    trainer_classes: List[TrainerClass], levelup_moves: dict, name_map: dict
) -> None:
    """
    Populates the move sets for Pokémon in each trainer class based on their level and level-up moves.

    Args:
        trainer_classes (List[TrainerClass]): A list of TrainerClass objects that contain trainers and Pokémon.
        levelup_moves (dict): A dictionary where keys are Pokémon names and values are lists of tuples
                               (level, move) representing the level at which a Pokémon learns a move.
        name_map (dict): Mapping of gen 1 names (UPPER CASE) to engine names
    """
    # Iterate through each trainer class
    for trainer_class in trainer_classes:
        # Iterate through each trainer in the class
        for trainer in trainer_class.trainers:
            # Iterate through each Pokémon that the trainer owns
            for pokemon in trainer.pokemon:
                if (
                    pokemon_species := correct_pokemon_name(pokemon.species)
                ) not in levelup_moves:
                    continue  # Skip if there's no level-up learnset for this species

                # Extract the moves that the Pokémon would have learned at or before the given level
                pokemon_moves = [
                    move
                    for move_level, move in levelup_moves[pokemon_species]
                    if move_level <= pokemon.extra["level"]
                ]

                # Get the last 4 moves learned
                pokemon_moves = pokemon_moves[-4:]  # Keep only the last 4 moves

                # Assign the moves to the Pokémon's moves attribute
                pokemon.moves = tuple(pokemon_moves)
                pokemon.species = name_map[pokemon.species.upper()]


if __name__ == "__main__":
    """
    Load party data (without levels)
    Load learnset moves
    Then patch last four learned moves in and save

    TODO: Patch E4 + Gym moves
    """

    with open("asm/parties.asm", "r") as f:
        trainer_class_data = f.read()
    with open("asm/evos_moves.asm", "r") as f:
        learnset_asm = f.read()
    with open("asm/dex.asm", "r") as f:
        dex_asm = f.read()
    with open("asm/moves.asm", "r") as f:
        moves_asm = f.read()
    base_stats_folder = "asm/base_stats"

    with open("asm/move_choices.asm", "r") as f:
        move_choices_asm = (
            f.read()
        )  # Assume stability of dict as we only use the values
    move_choices = list(parse_move_choices(move_choices_asm).values())

    # Grab trainer data
    trainer_classes = parse_trainer_data(trainer_class_data)[1:]
    for idx, trainer_class in enumerate(trainer_classes):
        trainer_class.modifiers = move_choices[idx]
        for trainer in trainer_class.trainers:
            trainer.modifiers = move_choices[idx]

    # Step 1: Parse learnset data
    learnset_moves = parse_learnset_moves(learnset_asm)

    # Step 2: Parse level 1 moves from base stats
    level1_moves = parse_level1_moves(base_stats_folder)

    # Step 3: Combine the moves - Needs renaming
    _levelup_moves = combine_moves(learnset_moves, level1_moves)

    # Step 4: Rename moves
    _moves_data = parse_moves(moves_asm)
    moves_data = dict(zip(MOVES, _moves_data.values()))
    # Create remap for moves to correct their spelling
    moves_map = dict(zip(_moves_data.keys(), MOVES))
    # And remap for pokemon
    name_map = dict(zip(parse_dex_data(dex_asm).keys(), SPECIES.keys()))

    levelup_moves = {
        pokemon: [(level, moves_map[move]) for level, move in moves]
        for pokemon, moves in _levelup_moves.items()
    }

    # Add in moves
    populate_trainer_moves(trainer_classes, levelup_moves, name_map)

    # Correct pokemon names here
    # print(trainer_classes)

    # Dump data, don't include 0th trainer which is empty
    serialize_trainerclasses(trainer_classes, "data/trainerclasses.pkl")

    with open("data/moves.json", "w") as f:
        json.dump(moves_data, f)
