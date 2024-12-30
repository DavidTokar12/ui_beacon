from __future__ import annotations

import pytest

from ui_beacon_lang import UiBeaconFileNotFoundError
from ui_beacon_lang import UiBeaconValidationError


def test_include_without_href(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_include_with_addional_attributes(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_included_page_not_found(parser, input_app_file):
    with pytest.raises(UiBeaconFileNotFoundError):
        parser.parse(input_app_file)


def test_included_page_invalid(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)
