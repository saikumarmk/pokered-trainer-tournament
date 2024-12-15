
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

After all your dependencies have been installed, you can regenerate the `trainerclasses.pkl` file by running:

```bash
python -m utils.parse_asm
```

## Generating results

You can simply run `python run_battle.py` to simulate all `391*390/2` battles, which will then be pickled. TBD on how to analyse these results, though you can just use `utils/elo_calculator.py` inside a notebook to get the rankings.