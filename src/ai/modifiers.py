import random
from pykmn.engine.gen1 import Battle, Player, Choice, Pokemon


type_effectiveness_chart = {
    ("Water", "Fire"): 2.0,
    ("Fire", "Grass"): 2.0,
    ("Fire", "Ice"): 2.0,
    ("Grass", "Water"): 2.0,
    ("Electric", "Water"): 2.0,
    ("Water", "Rock"): 2.0,
    ("Ground", "Flying"): 0.0,
    ("Water", "Water"): 0.5,
    ("Fire", "Fire"): 0.5,
    ("Electric", "Electric"): 0.5,
    ("Ice", "Ice"): 0.5,
    ("Grass", "Grass"): 0.5,
    ("Psychic", "Psychic"): 0.5,
    ("Fire", "Water"): 0.5,
    ("Grass", "Fire"): 0.5,
    ("Water", "Grass"): 0.5,
    ("Electric", "Grass"): 0.5,
    ("Normal", "Rock"): 0.5,
    ("Normal", "Ghost"): 0.0,
    ("Ghost", "Ghost"): 2.0,
    ("Fire", "Bug"): 2.0,
    ("Fire", "Rock"): 0.5,
    ("Water", "Ground"): 2.0,
    ("Electric", "Ground"): 0.0,
    ("Electric", "Flying"): 2.0,
    ("Grass", "Ground"): 2.0,
    ("Grass", "Bug"): 0.5,
    ("Grass", "Poison"): 0.5,
    ("Grass", "Rock"): 2.0,
    ("Grass", "Flying"): 0.5,
    ("Ice", "Water"): 0.5,
    ("Ice", "Grass"): 2.0,
    ("Ice", "Ground"): 2.0,
    ("Ice", "Flying"): 2.0,
    ("Fighting", "Normal"): 2.0,
    ("Fighting", "Poison"): 0.5,
    ("Fighting", "Flying"): 0.5,
    ("Fighting", "Psychic"): 0.5,
    ("Fighting", "Bug"): 0.5,
    ("Fighting", "Rock"): 2.0,
    ("Fighting", "Ice"): 2.0,
    ("Fighting", "Ghost"): 0.0,
    ("Poison", "Grass"): 2.0,
    ("Poison", "Poison"): 0.5,
    ("Poison", "Ground"): 0.5,
    ("Poison", "Bug"): 2.0,
    ("Poison", "Rock"): 0.5,
    ("Poison", "Ghost"): 0.5,
    ("Ground", "Fire"): 2.0,
    ("Ground", "Electric"): 2.0,
    ("Ground", "Grass"): 0.5,
    ("Ground", "Bug"): 0.5,
    ("Ground", "Rock"): 2.0,
    ("Ground", "Poison"): 2.0,
    ("Flying", "Electric"): 0.5,
    ("Flying", "Fighting"): 2.0,
    ("Flying", "Bug"): 2.0,
    ("Flying", "Grass"): 2.0,
    ("Flying", "Rock"): 0.5,
    ("Psychic", "Fighting"): 2.0,
    ("Psychic", "Poison"): 2.0,
    ("Bug", "Fire"): 0.5,
    ("Bug", "Grass"): 2.0,
    ("Bug", "Fighting"): 0.5,
    ("Bug", "Flying"): 0.5,
    ("Bug", "Psychic"): 2.0,
    ("Bug", "Ghost"): 0.5,
    ("Bug", "Poison"): 2.0,
    ("Rock", "Fire"): 2.0,
    ("Rock", "Fighting"): 0.5,
    ("Rock", "Ground"): 0.5,
    ("Rock", "Flying"): 2.0,
    ("Rock", "Bug"): 2.0,
    ("Rock", "Ice"): 2.0,
    ("Ghost", "Normal"): 0.0,
    ("Ghost", "Psychic"): 0.0,
    ("Fire", "Dragon"): 0.5,
    ("Water", "Dragon"): 0.5,
    ("Electric", "Dragon"): 0.5,
    ("Grass", "Dragon"): 0.5,
    ("Ice", "Dragon"): 2.0,
    ("Dragon", "Dragon"): 2.0,
}


"""
These are the only status inflicting moves that don't do damage.
BURN/FREEZE always inflict damage along with status.


Thunder Wave
Glare
Stun Spores
Toxic
Poison Powder
Poison Gas
Spore
Sleep Powder
Sing
Hypnosis
Lovely Kiss
"""

NON_DAMAGE_STATUS_MOVES = {
    "Thunder Wave",
    "Glare",
    "Stun Spores",
    "Toxic",
    "Poison Powder",
    "Poison Gas",
    "Spore",
    "Sleep Powder",
    "Sing",
    "Hypnosis",
    "Lovely Kiss",
}
BUFF_STATUS_MOVES = {
    "Meditate",
    "Sharpen",
    "Defense Curl",
    "Harden",
    "Withdraw",
    "Growth",
    "Double Team",
    "Minimize",
    "Pay Day",
    "Swift",
    "Growl",
    "Leer",
    "Tail Whip",
    "String Shot",
    "Flash",
    "Kinesis",
    "Sand-Attack",
    "SmokeScreen",
    "Conversion",
    "Haze",
    "Swords Dance",
    "Acid Armor",
    "Barrier",
    "Agility",
    "Amnesia",
    "Recover",
    "Rest",
    "Softboiled",
    "Transform",
    "Screech",
    "Light Screen",
    "Reflect",
}

BETTER_MOVES = {
    "Super Fang",
    "Dragon Rage",
    "Psywave",
    "Night Shade",
    "Seismic Toss",
    "SonicBoom",
    "Fly",
}

# Set move_pp = 999


# Deprio on status moves, store current pokemon slots
def mod1(battle: Battle, current_player: Player, moves_priorities: list[str]) -> None:
    """
    Penalises using a non-damaging status move if the opposing pokemon is status'd.

    I think I should pass in the battle class for pull out stuff. Though in the future
    this would be done with an interface so that we can swap to showdown engine. (IDK)

    Pull the condition of the current pokemon
    If in [PAR, SLEEP, POIS] then apply modifier:
            for each move, check if its in the above category
            if it is, increment by 5
    otherwise:
            return
    """
    other_pokemon_status = battle.status(1 - current_player, 1)
    if not other_pokemon_status.healthy():
        moves = battle.moves(current_player, "Active")
        for idx, move in enumerate(moves):
            if move in NON_DAMAGE_STATUS_MOVES:
                moves_priorities[idx] += 5


# Buff on round 2 (not round 1 as intended because the game is a buggy piece of sht)
def mod2(battle: Battle, current_player: Player, moves_priorities: list[str]) -> None:

    current_turn = battle.turn()
    if current_turn == 2:  # Implementing buggy off by one (should actually be one)
        moves = battle.moves(current_player, "Active")
        for idx, move in enumerate(moves):
            if move in BUFF_STATUS_MOVES:
                moves_priorities[idx] -= 1


"""
Alternatives:
Super Fang
Dragon Rage, Psywave, Night Shade, Seismic Toss, SonicBoom
Fly


"""


# High wisdom, low knowledge (good idiot ai)
def mod3(
    battle: Battle,
    current_player: Player,
    moves_priorities: list[int],
    moves_data: dict,
) -> None:
    """
    Adjust move priorities based on type effectiveness and better alternative moves.

    Penalises moves that are not very effective if there are better moves available.
    Encourages super-effective moves.
    """
    # Define better moves (effects or specific moves)
    # Get the moves for the current player
    moves = battle.moves(current_player, "Active")

    # Check if a "better move" exists
    better_move_found = any(move in BETTER_MOVES for move in moves)

    # Get the opponent's active Pokémon types
    defender_types = battle.active_pokemon_types(1 - current_player)
    defender_type = defender_types[0]

    # Adjust priorities for each move
    for idx, move in enumerate(moves):
        move_data = moves_data[move]
        move_type = move_data["type"]

        # Check type effectiveness using numeric values
        effectiveness = type_effectiveness_chart.get(
            (move_type, defender_type), 1.0
        )  # Default is 1.0 (neutral)
        if effectiveness > 1.0:
            moves_priorities[idx] -= 1  # Prioritize highly effective moves
        elif effectiveness < 1.0 and better_move_found:
            moves_priorities[
                idx
            ] += 1  # Penalize less effective moves if better moves exist

# TODO: Modify trainerai 3 to actually work and consider both types
def mod4(battle: Battle, current_player: Player, moves_priorities: list[str], moves_data: dict) -> None:
    """
    Mod4 modifies the AI's decision-making to account for both types of the attacking and defending Pokémon.
    It multiplies the type effectiveness values of both types for more accurate move selection.

    Arguments:
    - battle: The current battle state
    - current_player: The player making the move
    - moves_priorities: List of move priorities to be modified based on type effectiveness
    """

    # Get the types of the current player's Pokémon and the opponent's Pokémon
    enemy_types = battle.active_pokemon_types(1 - current_player)

    moves = battle.moves(current_player, "Active")
    better_move_found = any(move in BETTER_MOVES for move in moves)

    # Loop through each move and check its effectiveness
    for idx, move in enumerate():
        move_data = moves_data[move]
        move_type = move_data["type"]

        move_power = move_data["power"]

        # Multiply the type effectiveness for both enemy types
        type_effectiveness_1 = type_effectiveness_chart.get(move_type, enemy_types[0], 1.0)
        type_effectiveness_2 = type_effectiveness_chart.get(move_type, enemy_types[1], 1.0)
        combined_effectiveness = type_effectiveness_1 * type_effectiveness_2

        # Apply logic based on combined effectiveness
        if combined_effectiveness == 0.0:
            moves_priorities[idx] += 2  # Strongly discourage
        elif 0 < combined_effectiveness < 1 and better_move_found:
            moves_priorities[idx] += 1  # Weakly discourage
        elif combined_effectiveness > 1.0 and move_power > 1:
            moves_priorities[idx] -= 1  # Weakly encourage