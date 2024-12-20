"""Test script."""

from pykmn.engine.gen1 import Battle, Choice, Pokemon
from tqdm import tqdm
from pykmn.engine.common import ResultType, Slots
from pykmn.engine.protocol import parse_protocol
from ai.choice import advance_battle
import pickle
import itertools
from models.pokemon import deserialize_trainerclasses, Trainer, TrainerClass


def flatten(seq: list) -> list:
    return [element for subseq in seq for element in subseq]


def run_battle(trainer1: Trainer, trainer2: Trainer, log=True) -> ResultType:
    """Runs a Pokémon battle.

    Args:
        log (`bool`, optional): Whether to log protocol traces. Defaults to `True`.
    """
    team1 = trainer1.pokemon
    team2 = trainer2.pokemon

    battle = Battle(
        p1_team=team1,
        p2_team=team2,
    )
    slots: Slots = Slots(([p.species for p in team1], [p.species for p in team2]))

    # Turn 0
    (result, trace) = battle.update(Choice.PASS(), Choice.PASS())

    if log:
        print("---------- Battle setup ----------\nTrace: ")
        for msg in parse_protocol(trace, slots):
            print(f"* {msg}")

    choice = 1
    while result.type() == ResultType.NONE:
        if log:
            print(f"\n------------ Choice {choice} ------------")
        choice += 1

        (result, trace) = advance_battle(battle, result, trainer1, trainer2)

        if log:
            print("\nTrace:")
            for msg in parse_protocol(trace, slots):
                print("* " + msg)
        if choice > 1000:  # any stalling = tie
            return ResultType.TIE

    return result.type(), choice


if __name__ == "__main__":
    trainer_classes: list[TrainerClass] = deserialize_trainerclasses(
        "data/trainerclasses.pkl"
    )
    trainers = [
        trainer
        for trainer_class in trainer_classes
        for trainer in trainer_class.trainers
    ]

    #battles_to_run = list(itertools.product(trainers, trainers))
    battles_to_run = list(itertools.combinations(trainers, 2))
    
    battle_results = []
    for trainer, other_trainer in tqdm(battles_to_run):
        try:
            result, count = run_battle(trainer, other_trainer, False)
            battle_results.append(
                {
                    "player1": f"{trainer.name}-{trainer.location}",
                    "player2": f"{other_trainer.name}-{other_trainer.location}",
                    "outcome": result,
                }
            )
        except Exception as e:
            print(
                f"Error during battle between {trainer.name} and {other_trainer.name}: {e}"
            )
            battle_results.append(
                {
                    "player1": f"{trainer.name}-{trainer.location}",
                    "player2": f"{other_trainer.name}-{other_trainer.location}",
                    "outcome": ResultType.ERROR,
                }
            )


    with open("data/battle_results_combinations.pkl", "wb") as f:
        pickle.dump(battle_results, f)


    # with tqdm(total=len(trainers) ** 2) as pbar:
    #     for trainer in trainers:
    #         for other_trainer in trainers:
    #             try:
    #                 result, count = run_battle(trainer, other_trainer, False)
    #                 battle_results.append(
    #                     {
    #                         "player1": f"{trainer.name}-{trainer.location}",
    #                         "player2": f"{other_trainer.name}-{other_trainer.location}",
    #                         "outcome": result,
    #                     }
    #                 )
    #             except Exception as e:
    #                 print(
    #                     f"Error during battle between {trainer.name} and {other_trainer.name}: {e}"
    #                 )
    #                 battle_results.append(
    #                     {
    #                         "player1": f"{trainer.name}-{trainer.location}",
    #                         "player2": f"{other_trainer.name}-{other_trainer.location}",
    #                         "outcome": ResultType.ERROR,
    #                     }
    #                 )
    #             pbar.update(1)


