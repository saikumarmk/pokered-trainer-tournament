import pickle
import numpy as np
from sklearn import linear_model
from typing import List, Dict
from dataclasses import dataclass, field
from pykmn.engine.common import ResultType
from models.pokemon import deserialize_trainerclasses, Pokemon

@dataclass
class Trainer:
    name: str
    location: str
    pokemon: List[Pokemon] = field(default_factory=list)
    lr_elo: float = 1500.0  # Default LR Elo

def load_battle_results(filename: str) -> List[Dict]:
    """Loads battle results from a pickle file."""
    with open(filename, "rb") as f:
        return pickle.load(f)

def build_trainer_lookup(trainers: List[Trainer]) -> Dict[str, int]:
    """Builds a hashmap to map trainer 'name-location' to their index."""
    return {f"{trainer.name}-{trainer.location}": idx for idx, trainer in enumerate(trainers)}

def generate_lr_elo(battle_results: List[Dict], trainers: List[Trainer]):
    """Generates LR Elo scores for trainers based on battle results."""
    trainer_lookup = build_trainer_lookup(trainers)
    N = len(trainers)
    X = []
    Y = []

    for battle in battle_results:
        try:
            t1_id = battle["player1"]
            t2_id = battle["player2"]
            t1_idx = trainer_lookup[t1_id]
            t2_idx = trainer_lookup[t2_id]
            outcome = battle["outcome"]

            v = np.zeros(N)
            v[t1_idx] = 1
            v[t2_idx] = -1
            X.append(v)

            if outcome == ResultType.PLAYER_1_WIN:
                Y.append(1)
            elif outcome == ResultType.PLAYER_2_WIN:
                Y.append(0)
            elif outcome == ResultType.TIE:
                Y.append(1)
                Y.append(0)
                X.append(v)
        except KeyError:
            print(f"Trainer not found in lookup: {battle}")
            continue

    clf = linear_model.LogisticRegression()
    clf.fit(X, Y)
    return list(clf.coef_[0] * 173 + 1500), clf.intercept_[0]

def main():
    """Main function to calculate and display LR Elo scores."""
    trainers = deserialize_trainerclasses("data/trainerclasses.pkl")  # Assuming a similar deserialization
    trainers_flat = [trainer for trainer_class in trainers for trainer in trainer_class.trainers]

    battle_results = load_battle_results("battle_results.pkl")
    regression_elo, _ = generate_lr_elo(battle_results, trainers_flat)

    for i, trainer in enumerate(trainers_flat):
        trainer.lr_elo = regression_elo[i]

    # Print results
    trainers_flat.sort(key=lambda t: t.lr_elo)
    for trainer in trainers_flat:
        print(f"Trainer: {trainer.name} - {trainer.location}, LR Elo: {trainer.lr_elo}")

if __name__ == '__main__':
    main()
