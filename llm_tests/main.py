from __future__ import annotations

import argparse
import json
import logging
import os

from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from ui_beacon import StepPlannerResponse
from ui_beacon import create_system_prompts
from ui_beacon_lang import UiBeaconLangParser


def parse_arguments():
    argument_parser = argparse.ArgumentParser(
        description="Run AI tests for different suites.")
    argument_parser.add_argument(
        "suite", type=str, help="Test suite to run (e.g., gmail, outlook)."
    )
    argument_parser.add_argument(
        "--model", type=str, default="gpt-4o", help="Model to use for the tests."
    )
    argument_parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        help="Filter tests by difficulty.",
    )
    argument_parser.add_argument(
        "--ids", type=str, nargs="*", help="Specific test case IDs to run."
    )
    return argument_parser.parse_args()


def load_test_data(suite: str) -> dict:
    path = Path(__file__).parent / suite / f"{suite}_inputs.json"
    if not path.exists():
        logging.error(f"Test data not found: {path}")
        raise FileNotFoundError(f"Test data not found for suite: {suite}")
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def process_test_case(
    test_case,
    client,
    planner_system_prompt,
    plan_to_response_converter_system_prompt,
    model,
):
    user_prompt = json.dumps(test_case)

    try:
        plan_completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": planner_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            response_format=StepPlannerResponse,
        )

        plan_result: StepPlannerResponse = plan_completion.choices[0].message.parsed
        plan_result = plan_result.model_dump()

        plan_result_str = json.dumps(plan_result)

        conversion_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": plan_to_response_converter_system_prompt},
                {"role": "user", "content": plan_result_str},
            ],
            temperature=0.0,
        )
        conversion_result = conversion_completion.choices[0].message.content

        return {
            "conversion": conversion_result,
            "plan": plan_result,
        }
    except Exception as e:
        logging.error(f"Error processing case {test_case.get('id')}: {e!s}")


def run_tests(suite: str, model: str, difficulty: str | None, ids: list[str] | None):
    """
    Run tests for a given suite and model, optionally filtering by difficulty and test case IDs.

    Args:
        suite (str): The name of the test suite to run.
        model (str): The model to use for running the tests.
        difficulty (str | None): Optional difficulty level to filter test cases.
        ids (list[str] | None): Optional list of test case IDs to filter.

    Returns:
        None
    """
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    logging.info(f"Running tests for suite: {suite}, model: {model}")

    ui_beacon_code_path = Path(__file__).parent / \
        suite / f"{suite}_app.uibl"

    try:
        prompts = create_system_prompts(
            ui_beacon_code_path=ui_beacon_code_path)
        planer_system_prompt = prompts["planner_prompt"]
        plan_to_response_converter_prompt = prompts["plan_to_response_converter_prompt"]

    except Exception as e:
        logging.error(f"Error creating system prompt: {e}")
        return

    try:
        test_data = load_test_data(suite)
    except FileNotFoundError as e:
        logging.error(f"Error loading test data: {e!s}")
        return
    except Exception as e:
        logging.error(f"Unexpected error loading test data: {e!s}")
        return

    client = OpenAI()
    results = {diff: [] for diff in test_data}

    filtered_cases = [
        (case, diff)
        for diff, cases in test_data.items()
        if not difficulty or diff == difficulty
        for case in cases
        if not ids or case.get("id") in ids
    ]

    if not filtered_cases:
        logging.warning("No matching test cases found.")
        return

    with tqdm(total=len(filtered_cases), desc="Processing Test Cases") as pbar:
        for test_case, diff in filtered_cases:
            answer = process_test_case(
                test_case=test_case,
                client=client,
                planner_system_prompt=planer_system_prompt,
                plan_to_response_converter_system_prompt=plan_to_response_converter_prompt,
                model=model,
            )
            results[diff].append({"test_case": test_case, "response": answer})
            pbar.update(1)

    output_path = Path("test_results.json")
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(results, output_file, indent=2, ensure_ascii=False)
    logging.info(f"Test results saved to {output_path}")


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    args = parse_arguments()
    run_tests(args.suite, args.model, args.difficulty, args.ids)


if __name__ == "__main__":
    main()
