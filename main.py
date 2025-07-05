import package_generator
import click


@click.command("generate-packages")
@click.argument(
    "directory",
    default="./output",
    type=click.Path(dir_okay=True, file_okay=False, exists=False),
)
def generate_packages(directory):
    package_generator.build_package_dir(directory)


@click.group(name="solver")
def solver():
    pass


solver.add_command(generate_packages)

if __name__ == "__main__":
    solver()
