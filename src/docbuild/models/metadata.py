"""Module for defining the Metadata model."""

from pathlib import Path
import re
from typing import ClassVar, Self
from dataclasses import dataclass, field


@dataclass
class Metadata:
    """A class to represent the metadata of a deliverable."""
    title: str | None = field(default=None)
    subtitle: str = field(default="")
    #
    seo_title: str | None = field(default=None)
    seo_description: str = field(default="")
    seo_social_descr: str = field(default="")
    #
    dateModified: str = field(default="")
    tasks: list[str] = field(default_factory=list)
    series: str | None = field(default=None)
    rootid: str | None = field(default=None)
    #
    # description: str | None = field(default=None)
    products: list[dict] = field(default_factory=list)
    # docTypes: list[str] | None = field(default=None)
    # archives: list[str] | None = field(default=None)
    # category: str | None = field(default=None)
    #
    _match: ClassVar[re.Pattern] = re.compile(r"\[(.*?)\](.*)")

    def read(self, metafile: Path|str) -> Self:
        """
        Read the metadata from a file
        """
        lines = Path(metafile).open().readlines()
        for line in lines:
            if line.lstrip().startswith("#"):
                continue
            key, value = map(str.strip, line.split("=", 1))

            match key:
                # case "category":
                #     if value:
                #         self.category = value
                case "title":
                    self.title = value

                case "subtitle":
                    if value:
                        self.subtitle = value

                case "seo-title":
                    if value:
                        self.seo_title = value

                case "seo-social-descr":
                    if value:
                        self.seo_social_descr = value

                case "seo-description":
                    if value:
                        self.seo_description = value

                case "date":
                    if value:
                        self.dateModified = value

                case "rootid":
                    if value:
                        self.rootid = value

                case "task":
                    self.tasks = [task.strip() for task in value.split(";")]

                case "productname":
                    productlist = [entry["name"] for entry in self.products]
                    if mtch := self._match.match(value):
                        versions = mtch.group(1).strip().split(";")
                        product = mtch.group(2).strip()

                        dct = {"name": product,
                               "versions": versions,
                               }
                        self.products.append(dct)

                case "series":
                    if value:
                        self.series = value

        return self
