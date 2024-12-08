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
    name: str
    location: str
    pokemon: List[Pokemon] = field(default_factory=list)
    modifiers: tuple[int] = ()


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
