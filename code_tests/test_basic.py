from __future__ import annotations

import pytest

from ui_beacon_lang import UiBeaconFileNotFoundError
from ui_beacon_lang import UiBeaconValidationError


def test_parse_not_existing_file(parser):
    with pytest.raises(UiBeaconFileNotFoundError):
        parser.parse("not_existing_file")


def test_empty_file(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_minimal_app(parser, input_app_file):
    parser.parse(input_app_file)


def test_minimal_page(parser, input_page_file):
    parser.parse(input_page_file)


def test_invalid_xml(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_all_components_minimal_attributes(parser, input_app_file):
    parser.parse(input_app_file)


def test_all_components_maximal_attributes(parser, input_app_file):
    parser.parse(input_app_file)


def test_page_name_does_not_end_with_page(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)
