import os.path
import subprocess
from pathlib import Path
from typing import Any
import shutil

import toml
from tqdm.contrib.concurrent import thread_map

from templates import PREFIX, BUILD_BACKEND
from words import WORD_IDS, WORDS

LETTERS = "abcdefghijklmnopqrstuvwxyz"
INDEX = "./output/index"


def get_feedback_package_name(letter: str, positions: list[int]) -> str:
    return f"{PREFIX}{letter}_in_{''.join(str(p) for p in positions)}"


def get_feedback_package_version(is_true: bool) -> str:
    return "1.0.0" if is_true else "0.0.0"


def get_possible_position_package_name(letter: str) -> str:
    return f"{PREFIX}{letter}_poss"


def encode_position_mask(positions: list[int]) -> int:
    mask = 0
    for i in range(1, 6):
        mask = mask << 1
        if i in positions:
            mask = mask | 0x1
    return mask


def decode_position_mask(encoded_position: int) -> list[int]:
    return [i for i in range(1, 6) if encoded_position & (1 << (5 - i))]


def get_possible_position_package_version(positions: list[int]) -> str:
    return f"{encode_position_mask(positions)}.0.0"


def get_exact_position_package_name(position: int) -> str:
    return f"{PREFIX}pos_{position}"


def get_exact_position_package_version(letter: str) -> str:
    return f"{ord(letter) - ord('a') + 1}.0.0"


def emit_feedback_package(
    letter: str, encoded_positions: int, is_true: bool
) -> dict[str, Any]:
    package: dict[str, Any] = {"project": {}}
    package["project"]["name"] = get_feedback_package_name(
        letter, decode_position_mask(encoded_positions)
    )
    package["project"]["version"] = get_feedback_package_version(is_true)
    package.update(**BUILD_BACKEND)

    # Emit dependencies: include all position package versions where at least
    # one version overlaps with us (or none overlap with us if we're not supposed to match)

    # Unfortunately, we can't do ORs in dependency specs in Python, so instead
    # we flip it and instead of doing ==1.0.0, ==2.0.0, we do !=3.0.0, !=4.0.0 etc

    not_allowed_versions = [
        v for v in range(32) if not (bool(v & encoded_positions) ^ (not is_true))
    ]
    package["project"]["dependencies"] = [
        get_possible_position_package_name(letter)
        + " "
        + ",".join(f"!={v}.0.0" for v in not_allowed_versions)
    ]

    return package


def emit_possible_position_package(letter: str, encoded_version: int) -> dict[str, Any]:
    package: dict[str, Any] = {"project": {}}
    package["project"]["name"] = get_possible_position_package_name(letter)
    package["project"]["version"] = f"{encoded_version}.0.0"
    package.update(**BUILD_BACKEND)
    return package


def emit_exact_position_package(letter: str, position: int) -> dict[str, Any]:
    package: dict[str, Any] = {"project": {}}
    package["project"]["name"] = get_exact_position_package_name(position)
    package["project"]["version"] = get_exact_position_package_version(letter)
    package.update(**BUILD_BACKEND)

    mask = 1 << (5 - position)
    not_allowed_versions = [v for v in range(32) if not bool(v & mask)]
    package["project"]["dependencies"] = [
        get_possible_position_package_name(letter)
        + " "
        + ",".join(f"!={v}.0.0" for v in not_allowed_versions)
    ]

    # We also need to exclude any other letters from this position
    other_letter_not_allowed_versions = [v for v in range(32) if bool(v & mask)]
    other_letter_spec = ",".join(
        f"!={v}.0.0" for v in other_letter_not_allowed_versions
    )
    package["project"]["dependencies"].extend(
        [
            get_possible_position_package_name(other_letter) + " " + other_letter_spec
            for other_letter in LETTERS
            if other_letter != letter
        ]
    )

    return package


def emit_word_package(word: str) -> dict[str, Any]:
    package: dict[str, Any] = {"project": {}}
    package["project"]["name"] = f"{PREFIX}word"
    package["project"]["version"] = f"{WORD_IDS[word]}.0.0"
    package.update(**BUILD_BACKEND)

    # Emit dependencies on exact position packages, e.g.
    # 'weird' -> pos_1 = w, pos_2 = e, ... pos_5 = d
    package["project"]["dependencies"] = [
        f"{get_exact_position_package_name(pos + 1)} =={get_exact_position_package_version(letter)}"
        for pos, letter in enumerate(word)
    ]
    return package


def write_package_content(directory: str, package_name: str, package: dict[str, Any]):
    package_path = Path(directory) / "src" / Path(package_name)
    package_path.mkdir(exist_ok=True, parents=True)
    with open(os.path.join(directory, "pyproject.toml"), "w") as f:
        toml.dump(package, f)
    with open(
        os.path.join(package_path, "__init__.py"),
        "w",
    ) as _:
        pass


def build_package_dir(directory):
    # Build word packages
    for word in WORDS:
        version_dir = os.path.join(directory, f"{PREFIX}word-{WORD_IDS[word]}.0.0")
        write_package_content(version_dir, f"{PREFIX}word", emit_word_package(word))

    # Build exact position packages
    for letter in LETTERS:
        for position in range(1, 6):
            package_name = get_exact_position_package_name(position)
            version_dir = os.path.join(
                directory,
                f"{package_name}-{get_exact_position_package_version(letter)}",
            )
            write_package_content(
                version_dir, package_name, emit_exact_position_package(letter, position)
            )

    # Build possible position packages
    for letter in LETTERS:
        for encoded_version in range(0, 32):
            package_name = get_possible_position_package_name(letter)
            version_dir = os.path.join(
                directory,
                f"{package_name}-{encoded_version}.0.0",
            )
            write_package_content(
                version_dir,
                package_name,
                emit_possible_position_package(letter, encoded_version),
            )

    # Build feedback packages
    for letter in LETTERS:
        for encoded_position in range(1, 32):
            for is_true in [True, False]:
                package_name = get_feedback_package_name(
                    letter, decode_position_mask(encoded_position)
                )
                version_dir = os.path.join(
                    directory,
                    f"{package_name}-{get_feedback_package_version(is_true)}",
                )
                write_package_content(
                    version_dir,
                    package_name,
                    emit_feedback_package(letter, encoded_position, is_true),
                )


def publish_packages(directory):
    try:
        shutil.rmtree(os.path.join(directory, "wheels"))
    except FileNotFoundError:
        pass

    def _work(v: str) -> None:
        subprocess.check_call(
            [
                "uv",
                "build",
                "-o",
                "../wheels",
            ],
            cwd=v,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    dirs = [os.path.join(directory, d) for d in os.listdir(directory)]
    thread_map(_work, dirs)
