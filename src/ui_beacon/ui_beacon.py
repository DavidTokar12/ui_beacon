from __future__ import annotations

from pathlib import Path
from xml.etree import ElementInclude
from xml.etree import ElementTree

from ui_beacon.utils import read_prompt_schema


def validate_ui_beacon_lang_code(ui_beacon_code: str) -> None:
    """
    Validate the given UI Beacon language code.

    Args:
        ui_beacon_lang_code: The UI Beacon language code to validate.
    """

    if not ui_beacon_code:
        raise ValueError("The UI Beacon language code cannot be empty.")

    return None


def load_ui_beacon_code(code_path: str | Path) -> str:
    try:
        path = Path(code_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        tree = ElementTree.parse(path)
        root = tree.getroot()

        ElementInclude.include(root, base_url=str(path))

        return ElementTree.tostring(root, encoding="unicode")

    except Exception as e:
        raise Exception(f"Error loading UI Beacon code: {e}")


def create_system_prompts(ui_beacon_code_path: str | Path) -> str:
    try:
        ui_beacon_code = load_ui_beacon_code(ui_beacon_code_path)
        validate_ui_beacon_lang_code(ui_beacon_code)

        planner_prompt_schema: str = read_prompt_schema("planner_system.md")
        planner_prompt = planner_prompt_schema.format(ui_beacon_code=ui_beacon_code)

        plan_to_response_converter_prompt: str = read_prompt_schema(
            "plan_to_response_converter_system.md"
        )

        return {
            "planner_prompt": planner_prompt,
            "plan_to_response_converter_prompt": plan_to_response_converter_prompt,
        }
    except Exception as e:
        raise Exception(f"Error creating system prompt schema: {e}")
