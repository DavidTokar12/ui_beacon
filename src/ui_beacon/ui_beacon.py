from __future__ import annotations

from typing import TYPE_CHECKING

from ui_beacon.utils import read_prompt_schema
from ui_beacon_lang import UiBeaconLangParser


if TYPE_CHECKING:
    from pathlib import Path


def create_system_prompts(ui_beacon_code_path: str | Path) -> str:
    try:
        ui_beacon_code = UiBeaconLangParser().parse(ui_beacon_code_path)

        planner_prompt_schema: str = read_prompt_schema("planner_system.md")
        planner_prompt = planner_prompt_schema.format(
            ui_beacon_code=ui_beacon_code)

        plan_to_response_converter_prompt: str = read_prompt_schema(
            "plan_to_response_converter_system.md"
        )

        return {
            "planner_prompt": planner_prompt,
            "plan_to_response_converter_prompt": plan_to_response_converter_prompt,
        }
    except Exception as e:
        raise Exception(f"Error creating system prompt schema: {e}")
