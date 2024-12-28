from __future__ import annotations

import os

from pathlib import Path


def get_prompt_schema_file_path(prompt_file_name: str) -> Path:
    """
    Get the path to the prompt file with the given name.

    Args:
        prompt_file_name: The name of the prompt file.
    """

    path = Path(
        os.path.join(os.path.dirname(__file__), "assets", "prompts", prompt_file_name)
    )

    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    return path


def read_prompt_schema(prompt_file_name: str) -> str:
    """
    Read the prompt schema from the given file.

    Args:
        prompt_file_name: The name of the prompt file.
    """

    path = get_prompt_schema_file_path(prompt_file_name)

    with open(path, encoding="utf-8") as file:
        prompt = file.read()

    return prompt
