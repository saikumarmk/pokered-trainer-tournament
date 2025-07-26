from dataclasses import dataclass, field
from typing import List
import pickle


@dataclass
class Pokemon:
    extra: dict
    species: str
    moves: tuple[str] = ()


@dataclass
class Trainer:
    """
    Data structure for a Pokémon Trainer and their LR Elo.

    name: Trainer's name
    location: In-game location of the trainer
    pokemon: List of their Pokémon (could be used for features)
    lr_elo: Logistic Regression Elo rating (starts at 1500)
    """

    name: str
    location: str
    pokemon: list[Pokemon] = field(default_factory=list)
    lr_elo: float = 1500.0
    win: int = 0
    loss: int = 0
    draw: int = 0
    


@dataclass
class TrainerClass:
    name: str
    trainers: List[Trainer] = field(default_factory=list)
    modifiers: tuple[int] = ()


def serialize_trainerclasses(trainerclasses: List[TrainerClass], filename: str):
    with open(filename, "wb") as f:
        pickle.dump(trainerclasses, f)


# Deserialize the list of TrainerClass objects
def deserialize_trainerclasses(filename: str) -> List[TrainerClass]:
    with open(filename, "rb") as f:
        return pickle.load(f)
