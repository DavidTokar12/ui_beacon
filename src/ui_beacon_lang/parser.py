from __future__ import annotations

import os
import re

from pathlib import Path

from lxml import etree


class UiBeaconLangParser:

    def __init__(self):
        self.xsd_path = Path(__file__).parent / "ui_beacon_validator.xsd"

        if not self.xsd_path.exists():
            raise FileNotFoundError(f"XSD file not found: {self.xsd_path}")

        self.schema = etree.XMLSchema(etree.parse(str(self.xsd_path)))

    def parse(self, path: str | Path):
        """
        Main entry point to parse a .uibl file and produce
        valid XML (as a string) with the required prolog and transforms.

        Args:
            path (str | Path): Path to the .uibl file to parse.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.name.endswith("_website.uibl"):
            return self.__parse_website(path)
        elif path.name.endswith("_page.uibl"):
            return self.__parse_page(path)
        else:
            raise ValueError(
                f"File '{
                    path}' doesn't look like either a website or page file. It doesn't end with either '_website.uibl' or '_page.uibl'."
            )

    def __parse_website(self, path: str | Path) -> str:
        """
        - Ensures the root element is <Website>.
        - Adds XML prolog and DOCTYPE.
        - Transforms <IncludePage href="something.uibl" /> to <xi:include href="something.xml" parse="xml" />.

        Args:
            data (str): The raw data from the .uibl file.
        """

        try:
            website_root = self.__load_and_clean_xml(path)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML Parse Error in website file {path}: {e}")

        if website_root.tag != "Website":
            raise ValueError(
                f"Root element must be <Website>, found <{
                    website_root.tag}> instead."
            )

        self.__load_page_includes(path=path, root=website_root)

        self.__validate(path=path, root=website_root)

        return etree.tostring(
            website_root,
            pretty_print=True,
            encoding="unicode",
            doctype="<!DOCTYPE xml>",
        )

    def __load_page_includes(self, path: str | Path, root: etree.Element) -> None:
        """
        Iterates over all <IncludePage> elements in the given root element, validates the page path, validates the page XML, then replaces the element with the parsed XML.

        Args:
            path (str | Path): The path to the main Website file.
            root (etree.Element): The root element of the main Website file.
        """

        for include in root.xpath("//IncludePage"):
            include: etree.Element

            line_number = include.sourceline
            element_string = etree.tostring(include, encoding="unicode")

            href = include.get("href")

            if not href:
                raise ValueError(
                    f"In the Website file {path} the {element_string} element at line {
                        line_number} is missing 'href' attribute."
                )

            if len(include.attrib) > 1:
                raise ValueError(
                    f"In the Website file {path} the {element_string} element at line {
                        line_number} has unexpected attributes."
                )

            page_path = os.path.join(path.parent, href)
            page_element = self.parse(page_path)

            parent = include.getparent()
            parent.replace(include, page_element)

    def __parse_page(self, path: str | Path) -> etree.Element:
        """
        - Ensures the root element is <Page>.
        - Ensures it is valid XML following Page schema.
        """

        try:
            page_root = self.__load_and_clean_xml(path)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML Parse Error in page file {path}: {e}")

        if page_root.tag != "Page":
            raise ValueError(
                f"In {path}: Root element must be <Page>, found <{
                    page_root.tag}> instead."
            )

        self.__validate(path=path, root=page_root)
        return page_root

    def __validate(self, path, root: etree.Element) -> None:
        if not self.schema.validate(root):
            raise ValueError(f"Validation Error in page file {
                             path}: {self.schema.error_log}")

    def __load_and_clean_xml(self, path: str | Path) -> etree.Element:
        try:
            with open(path, encoding="utf-8") as f:
                xml_data = f.read()
            # clean up special characters: & -> &amp; etc.
            xml_data = re.sub("&(?!amp;)", "&amp;", xml_data)
            parser = etree.XMLParser(remove_blank_text=True)
            return etree.fromstring(xml_data, parser)
        except Exception as e:
            raise ValueError(f"XML Parse Error in {path}: {e}")


parser = UiBeaconLangParser()

with open("/workspaces/ui_beacon/test.xml", mode="w") as f:
    f.write(parser.parse("/workspaces/ui_beacon/tests/gmail/ui_beacon_website.uibl"))
