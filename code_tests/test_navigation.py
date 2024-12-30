from __future__ import annotations

import pytest

from ui_beacon_lang import UiBeaconValidationError


def test_navigation_to_none_existing_page(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_navigation_to_own_page(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)
