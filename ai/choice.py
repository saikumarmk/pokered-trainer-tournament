from typing import Callable
import random
from pykmn.engine.gen1 import Battle, Player, Choice, ChoiceType
from pykmn.engine.common import ResultType, Result
from ai.modifiers import mod1, mod2, mod3
from functools import partial
from json import load
from models.pokemon import Trainer

with open("data/moves.json") as f:
    moves_data = load(f)

modifier_map = {
    1: mod1,
    2: mod2,
    3: partial(mod3, moves_data=moves_data),
}  # Ideally pack this data higher up


def decide_action(
    battle: Battle, current_player: Player, result, move_ai: tuple[Callable]
) -> Choice:
    """
    Does player turn selection through FFI using blah blah
    Check if we have any choices (pass battle)
    Then check if we can only switch out

    """
    move_priorities = [100 for _ in range(4)]  # initialise with all very very high prio
    moves_available = False
    choices = battle.possible_choices(current_player, result)
    move_choices = {}

    if len(choices) == 1:
        return choices[0]

    for choice in choices:
        match choice.type():
            case ChoiceType.MOVE:
                if choice.data() == 0:
                    return choice
                move_priorities[choice.data() - 1] = (
                    10  # If we can use it, set it back to normal prio
                )
                move_choices[choice.data() - 1] = choice
                moves_available = True

            case (
                ChoiceType.SWITCH
            ):  # Could be implementation detail for some NPC/extension
                pass
            case _:  # No options
                pass

    if not moves_available:
        return choices[0]

    # Now determine modifiers
    for move_mod in move_ai:
        move_mod(battle, current_player, move_priorities)

    # Randomly choose the moves with the highest priority (read min value)
    max_prio = min(move_priorities)
    return move_choices[
        random.choice(
            [
                idx
                for idx, move_prio in enumerate(move_priorities)
                if move_prio == max_prio
            ]
        )
    ]


def advance_battle(
    battle: Battle, result: ResultType, trainer1: Trainer, trainer2: Trainer
) -> tuple[Result, list[int]]:

    p1_choice = decide_action(
        battle, Player.P1, result, (modifier_map[val] for val in trainer1.modifiers)
    )
    p2_choice = decide_action(
        battle, Player.P2, result, (modifier_map[val] for val in trainer2.modifiers)
    )

    return battle.update(p1_choice, p2_choice)
