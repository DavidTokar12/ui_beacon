from __future__ import annotations

from pathlib import Path

import pytest

from ui_beacon_lang import UiBeaconLangParser


@pytest.fixture
def parser():
    parser = UiBeaconLangParser()
    return parser


def get_input_file(request, file_suffix):
    test_name = request.node.name
    file_path = Path(__file__).parent / "input_files" / \
        f"{test_name}_{file_suffix}.uibl"
    if file_path.exists():
        return file_path


@pytest.fixture
def input_app_file(request):
    return get_input_file(request, "app")


@pytest.fixture
def input_page_file(request):
    return get_input_file(request, "page")
