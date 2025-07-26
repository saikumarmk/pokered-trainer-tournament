
# Pokemon Gen 1 AI Trainer tournament

Code that uses the `pkmn/engine` and `PyKMN` to simulate a generation one trainer tournament. More details can be found in [this post](https://www.saikumarmk.com/pokered-elo/).


## Installation

Begin by setting up a virtual environment.

You will require the PyKMN bindings from [saikumarmk/PyKMN](https://github.com/saikumarmk/PyKMN) before proceeding. Clone the repository, and run the following in the `PyKMN` folder:

```bash
python3 -m build 
python3 -m pip install --find-links=dist pykmn
```

Which will generate the wheels for `pykmn` then install them. You should build this inside the virtual environment, although you could run the first command and then manually install the wheel. Up to you.

## Instructions

Generate trainer data, run the tournament and then do analysis.

## Generating Trainer Files

If you don't specify the level, it defaults to their usual levels.

```
python -m src.main gen trainer_path --set-level 100
```

## Simulate Tournament


```
python -m src.main tourney trainer_path battle_path
```

## Elo calculation

```
python -m src.main elo trainer_path battle_path
```

## E2E Example

If you want to do everything at once, use `e2e`:

```
python -m src.main e2e "data/new.pkl" "data/battle.pkl" 
```
