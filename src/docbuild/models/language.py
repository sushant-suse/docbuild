import re
from typing import ClassVar

from pydantic import BaseModel, computed_field
from pydantic.functional_validators import field_validator

from ..constants import ALLOWED_LANGUAGES


# Old definition:
# Language allows all the definied languages, but also "*" (=ALL).
# We only define "ALL" as uppercase to denote a constant, the rest is lowercase.
# Language = StrEnum(
#     "Language",
#     # The dict is mapped like "de_de": "de-de"
#     {"ALL": "*"} | {item.replace("-", "_"): item
#                     for item in sorted(ALLOWED_LANGUAGES)},
# )

class LanguageCode(BaseModel):
    """The language in the format language-country (all lowercase)

    It accepts also an underscore as a separator instead of a dash.
    Use "*" to denote "ALL" languages
    """

    language: str
    # = Field(
    #     pattern=r"^\*|(([a-z]{2})-([a-z]{2}))$",
    #     title="The language and country (or '*' for ALL)",
    #     # default="en-us",
    #     repr=True,
    # )

    ALLOWED_LANGS: ClassVar[frozenset] = frozenset(
        {"*"} | ALLOWED_LANGUAGES
    )

    def __init__(self, language, **kwargs):
        super().__init__(language=language, **kwargs)
        if language == "*":
            self._lang, self._country = ("*", "*")
        else:
            self._lang, self._country = re.split(r"[_-]", language)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value):
        """Check if the passed language adheres to the allowed language"""
        value = value.replace("_", "-")
        if value not in cls.ALLOWED_LANGS:
            raise ValueError(
                (f"Invalid language code '{value}'. "
                 f"Expected one of {', '.join(sorted(cls.ALLOWED_LANGS))}"),
            )
        return value

    @computed_field(
        repr=False,
        title="The language part of the language code",
        examples=["en", "de", "ja"]
    )
    def lang(self) -> str:
        """Extracts the language part of the language code
        (property)
        """
        return self._lang

    @computed_field(
        repr=False,
        title="The country part of the language code",
        examples=["us", "de", "jp"],
    )
    def country(self) -> str:
        """Extracts the country part of the language code
        (property)
        """
        return self._country
