from __future__ import annotations

import os
import re

from pathlib import Path
from typing import Union

from lxml import etree


class UiBeaconError(Exception):
    """Base error class for UIBeaconLangParser-related errors."""


class UiBeaconFileNotFoundError(FileNotFoundError, UiBeaconError):
    """Raised when a required .uibl file is not found."""


class UiBeaconValidationError(ValueError, UiBeaconError):
    """Raised when there is a validation or parsing error in UIBeaconLang."""


class UiBeaconLangParser:
    """Parser and validator for UIBeaconLang .uibl files."""

    def __init__(self) -> None:
        """
        Initializes the parser by loading and compiling the XML Schema definition.

        Raises:
            UiBeaconFileNotFoundError: If the XSD schema file is not found.
        """
        self.xsd_path = Path(__file__).parent / "ui_beacon_validator.xsd"

        if not self.xsd_path.exists():
            raise UiBeaconFileNotFoundError(
                f"XSD file not found: {self.xsd_path}"
            )

        try:
            self.schema = etree.XMLSchema(etree.parse(str(self.xsd_path)))
        except (etree.XMLSyntaxError, etree.XMLSchemaError) as e:
            raise UiBeaconValidationError(
                f"Failed to parse or compile the XSD schema at {
                    self.xsd_path}: {e}"
            )

    def parse(self, path: str | Path, return_format: str = "string") -> str | etree.Element:
        """
        Parses a .uibl file (either App or Page) and returns the validated XML as a string.

        Args:
            path (Union[str, Path]): Path to the .uibl file to parse.
            return_format (str): The format to return the parsed XML in. Either 'string' or 'element'.

        Returns:
            str | etree.Element: The validated XML as a string or Element.

        Raises:
            UiBeaconFileNotFoundError: If the .uibl file does not exist.
            UiBeaconValidationError: If the file extension or content is invalid.
        """
        path = Path(path)
        if not path.exists():
            raise UiBeaconFileNotFoundError(
                f"File {path} not found."
            )

        if path.name.endswith("_app.uibl"):
            app_root = self._parse_app(path)
            return app_root if return_format == "element" else etree.tostring(
                app_root, pretty_print=True, encoding="unicode",
                doctype="<!DOCTYPE xml>"
            )
        elif path.name.endswith("_page.uibl"):
            page_root = self._parse_page(path)
            return page_root if return_format == "element" else etree.tostring(
                page_root, pretty_print=True, encoding="unicode",
            )
        else:
            raise UiBeaconValidationError(
                f"In file '{
                    path}': File does not end with either '_app.uibl' or '_page.uibl'."
            )

    def _parse_app(self, path: Path) -> str:
        """
        Loads and validates an App (.uibl) file, including any <IncludePage> directives.

        Args:
            path (Path): The path to the main App file.

        Returns:
            str: The fully expanded and validated XML.

        Raises:
            UiBeaconValidationError: If the root element isn't <App> or if schema validation fails.
        """
        try:
            app_root = self._load_and_clean_xml(path)
        except etree.XMLSyntaxError as e:
            raise UiBeaconValidationError(
                f"XML syntax error in App file '{path}': {e}"
            )

        if app_root.tag != "App":
            raise UiBeaconValidationError(
                f"In file '{path}': Root element must be <App>, found <{
                    app_root.tag}> instead."
            )

        self._load_page_includes(path=path, root=app_root)
        self._validate_xml_schema(path=path, root=app_root)
        self._validate_navigation_paths(path=path, root=app_root)

        return app_root

    def _parse_page(self, path: Path) -> etree.Element:
        """
        Loads and validates a Page (.uibl) file.

        Args:
            path (Path): The path to the Page file.

        Returns:
            etree.Element: The root element for the Page.

        Raises:
            UiBeaconValidationError: If the root element isn't <Page> or if schema validation fails.
        """
        try:
            page_root = self._load_and_clean_xml(path)
        except etree.XMLSyntaxError as e:
            raise UiBeaconValidationError(
                f"XML syntax error in Page file '{path}': {e}"
            )

        if page_root.tag != "Page":
            raise UiBeaconValidationError(
                f"In file '{path}': Root element must be <Page>, found <{
                    page_root.tag}> instead."
            )

        self._validate_xml_schema(path=path, root=page_root)
        return page_root

    def _load_page_includes(self, path: Path, root: etree.Element) -> None:
        """
        Resolves <IncludePage> elements in an App file by parsing and inlining the referenced page.

        Args:
            path (Path): The path to the main App file.
            root (etree.Element): The root element of the main App file.

        Raises:
            UiBeaconValidationError: If <IncludePage> is missing 'href' or has unexpected attributes.
        """
        for include in root.xpath("//IncludePage"):
            line_number = include.sourceline
            element_string = etree.tostring(include, encoding="unicode")
            href = include.get("href")

            if not href:
                raise UiBeaconValidationError(
                    f"In file '{path}', line {line_number}: "
                    f"IncludePage element {
                        element_string} is missing 'href' attribute."
                )

            # Ensure no attributes other than href
            if len(include.attrib) > 1:
                raise UiBeaconValidationError(
                    f"In file '{path}', line {line_number}: "
                    f"IncludePage element {
                        element_string} has unexpected attributes."
                )

            page_path = os.path.join(path.parent, href)
            page_element = self.parse(page_path, return_format="element")

            parent = include.getparent()
            parent.replace(include, page_element)

    def _validate_xml_schema(self, path: Path, root: etree.Element) -> None:
        """
        Validates the given root element against the UIBeaconLang XSD schema.

        Args:
            path (Path): The path to the file being validated.
            root (etree.Element): The root element to validate.

        Raises:
            UiBeaconValidationError: If schema validation fails.
        """
        if not self.schema.validate(root):
            errors = []
            for error in self.schema.error_log:
                errors.append(
                    f"Line {error.line}, Column {
                        error.column}: {error.message}"
                )
            error_message = "\n".join(errors)
            raise UiBeaconValidationError(
                f"In file '{path}', schema validation failed:\n{error_message}"
            )

    def _validate_navigation_paths(self, path: Path, root: etree.Element) -> None:
        """
        Validates navigation targets in <Nav> elements to ensure they point to an existing Page.

        Args:
            path (Path): The path to the file being validated.
            root (etree.Element): The root element (App) to validate.

        Raises:
            UiBeaconValidationError: If page names are duplicated, or Nav points to a non-existent or self-referencing page.
        """
        page_names = set()
        navigation_pointers = []

        for page in root.xpath("//Page"):
            page_name = page.get("name")
            if not page_name.endswith("Page"):
                raise UiBeaconValidationError(
                    f"In file '{path}': Page name '{
                        page_name}' does not end with 'Page'."
                )

            if page_name in page_names:
                raise UiBeaconValidationError(
                    f"In file '{path}': Duplicate page name '{page_name}'."
                )

            page_names.add(page_name)

            for navigate in page.xpath(".//Nav"):
                element_string = etree.tostring(navigate, encoding="unicode")
                navigation_pointer = navigate.get("to")

                if navigation_pointer == page_name:
                    raise UiBeaconValidationError(
                        f"In file '{path}', within page '{page_name}': "
                        f"Nav element {element_string} points to itself."
                    )

                navigation_pointers.append(
                    (navigation_pointer, page_name, element_string))

        # After collecting all pointers, ensure they reference valid pages
        for pointer, page_name, element_string in navigation_pointers:
            if pointer not in page_names:
                raise UiBeaconValidationError(
                    f"In file '{path}', within page '{page_name}': "
                    f"Nav element {
                        element_string} points to a non-existent page: '{pointer}'."
                )

    def _load_and_clean_xml(self, path: Path) -> etree.Element:
        """
        Reads and cleans XML data from the given file path.

        Args:
            path (Path): The path to the XML file.

        Returns:
            etree.Element: The root element parsed from the cleaned XML file.

        Raises:
            UiBeaconValidationError: If any error occurs while reading or parsing the file.
        """
        try:
            with open(path, encoding="utf-8") as f:
                xml_data = f.read()
            # Convert & to &amp; if it's not already escaped
            xml_data = re.sub(r'&(?!amp;)', '&amp;', xml_data)
            parser = etree.XMLParser(remove_blank_text=True)
            return etree.fromstring(xml_data, parser)
        except Exception as e:
            raise UiBeaconValidationError(
                f"XML parse error in file '{path}': {e}"
            )
