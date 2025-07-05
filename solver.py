import subprocess
from pathlib import Path
from typing import Any

import toml

from package_generator import (
    get_feedback_package_name,
    get_feedback_package_version,
    PREFIX,
)
from words import WORDS

DepsList = list[tuple[str, list[int], bool]]


def feedback_to_deps(word: str, feedback: list[str]) -> DepsList:
    """
    Turn a word + feedback (a string like "GY..." where G is Green,
    Y is Yellow and . is blank) into a list of inferences about the
    word (e.g. A is in position 1, B is not in position 2)
    """
    result: DepsList = []

    # Go through green feedback: we guessed the letter at that
    # position and can just record that this position must contain
    # this letter.
    covered_by_green: set[int] = set()
    covered_by_yellow: set[int] = set()
    for i, (letter, letter_feedback) in enumerate(zip(word, feedback)):
        if letter_feedback == "G":
            result.append((letter, [i + 1], True))
            covered_by_green.add(i)

    # Go through yellow feedback: if a letter is yellow, it means that
    # it's not at that position but it's in one of positions that aren't
    # yet covered by green.
    for i, (letter, letter_feedback) in enumerate(zip(word, feedback)):
        if letter_feedback == "Y":
            result.append((letter, [i + 1], False))
            covered_by_yellow.add(i)
            possible_positions = [
                p + 1 for p in range(5) if p != i and p not in covered_by_green
            ]
            result.append((letter, possible_positions, True))

    # Go through blank feedback: if a letter is blank, it means that
    # it's not in any positions that aren't yet covered
    for i, (letter, letter_feedback) in enumerate(zip(word, feedback)):
        if letter_feedback == ".":
            positions = [
                p + 1
                for p in range(5)
                if p not in covered_by_green and p not in covered_by_yellow
            ]
            result.append((letter, positions, False))

    return result


def parse_feedback(text: str) -> list[str]:
    if len(text) != 5:
        raise ValueError("Wrong feedback format, must be 5 characters")

    result: list[str] = []
    for f in text.upper():
        if f not in ("Y", "G", "."):
            raise ValueError(
                "Wrong feedback format, each character must be one of G, Y, ."
            )
        result.append(f)
    return result


def make_problem_package(deps_list: DepsList) -> dict[str, Any]:
    package: dict[str, Any] = {"project": {}}
    package["project"]["name"] = "problem"
    package["project"]["version"] = "0.1.0"
    package["project"]["dependencies"] = ["wordle_word"] + [
        f"{get_feedback_package_name(letter, positions)} =={get_feedback_package_version(is_true)}"
        for letter, positions, is_true in deps_list
    ]

    return package


def exec_resolution(
    deps_list: DepsList, work_dir: str, wheels_dir: str, no_suppress: bool
) -> str | None:
    package = make_problem_package(deps_list)

    package_dir = Path(work_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    with open(package_dir / "pyproject.toml", "w") as f:
        package_toml = toml.dumps(package)
        f.write(package_toml)
    print("Generated package:")
    print(package_toml)

    # Execute resolution
    proc = subprocess.run(
        ["uv", "lock", "--find-links", wheels_dir],
        cwd=package_dir,
        stdout=None if no_suppress else subprocess.PIPE,
        stderr=None if no_suppress else subprocess.PIPE,
    )
    if proc.returncode != 0:
        output = proc.stderr.decode()
        if "project's requirements are unsatisfiable" in output:
            print("According to uv, project's requirements are unsatisfiable")
            return None
        else:
            # Reraise the error
            proc.check_returncode

    # Read the lockfile and get the version of the "word" package we're using
    with open(package_dir / "uv.lock") as f:
        lockfile = toml.load(f)
    word_stanza = [
        p for p in lockfile["package"] if p["name"] == f"{PREFIX.replace('_', '-')}word"
    ]
    if not word_stanza:
        raise ValueError("No word package in lockfile, something went wrong!")
    word_version = int(word_stanza[0]["version"].split(".")[0])
    word = WORDS[word_version]
    return word


def run_solver_loop(work_dir: str, wheels_dir: str, no_suppress: bool) -> None:
    current_deps_list: DepsList = []

    # Delete the lockfile so we start from scratch
    lockfile = Path(work_dir) / "uv.lock"
    if lockfile.exists():
        lockfile.unlink()

    while True:
        word = exec_resolution(current_deps_list, work_dir, wheels_dir, no_suppress)
        if not word:
            print("I give up!")
            return
        print(f"GUESS: {word}")
        while True:
            feedback_str = input("> ")
            try:
                feedback = parse_feedback(feedback_str)
                break
            except ValueError as e:
                print(f"Error: {e}")

        if all(c == "G" for c in feedback):
            print("Hooray!")
            return

        new_deps = feedback_to_deps(word, feedback)
        current_deps_list.extend(new_deps)
