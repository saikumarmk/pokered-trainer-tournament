from src.sim.run_tournament import run_tournament, run_tournament_cmd
from src.utils.elo_calculator import elo_calculator, elo_calculator_cmd
from src.utils.gen_trainer_data import gen_trainer_data, gen_trainer_data_cmd
import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("trainer_data_path")
@click.argument("battle_results_path")
@click.option("--set-level", default=None, type=int)
def e2e(trainer_data_path: str, battle_results_path: str, set_level: int | None = None):
    """
    Does an E2E run of the tournament.
    """
    gen_trainer_data(trainer_data_path, set_level)
    run_tournament(trainer_data_path, battle_results_path)
    elo_calculator(trainer_data_path, battle_results_path)


cli.add_command(gen_trainer_data_cmd,"gen")
cli.add_command(run_tournament_cmd,"tourney")
cli.add_command(elo_calculator_cmd,"elo")


if __name__ == "__main__":
    cli()
