from __future__ import annotations

import pytest

from ui_beacon_lang import UiBeaconValidationError


def test_correct_all_includes(parser, input_app_file):
    parser.parse(input_app_file)


def test_missing_header(parser, input_app_file):
    parser.parse(input_app_file)


def test_missing_page(parser, input_app_file):
    parser.parse(input_app_file)


def test_missing_footer(parser, input_app_file):
    parser.parse(input_app_file)


def test_incorrect_ordering(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_app_doesnt_start_with_app(parser, input_app_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_app_file)


def test_page_doesnt_start_with_page(parser, input_page_file):
    with pytest.raises(UiBeaconValidationError):
        parser.parse(input_page_file)
