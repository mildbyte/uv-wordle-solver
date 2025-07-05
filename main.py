import package_generator
import click
import solver


@click.command("generate-packages")
@click.argument(
    "directory",
    default="./output",
    type=click.Path(dir_okay=True, file_okay=False, exists=False),
)
def generate_packages(directory):
    print("Generating package project files...")
    package_generator.build_package_dir(directory)
    print("Building wheels...")
    package_generator.publish_packages(directory)


@click.command("run")
@click.argument(
    "project_dir",
    default="./problem",
    type=click.Path(),
)
@click.argument(
    "wheels_dir",
    default="../output/wheels",
    type=click.Path(),
)
def run_solver(project_dir, wheels_dir):
    solver.run_solver_loop(project_dir, wheels_dir)


@click.group(name="wordle_solver")
def wordle_solver():
    pass


wordle_solver.add_command(generate_packages)
wordle_solver.add_command(run_solver)

if __name__ == "__main__":
    wordle_solver()
