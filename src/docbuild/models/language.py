import re
from typing import ClassVar

from pydantic import BaseModel, Field, computed_field
from pydantic.errors import PydanticErrorMixin
from pydantic.functional_validators import field_validator

from ..constants import ALLOWED_LANGUAGES


class DocbuildModelValidationError(PydanticErrorMixin, ValueError):
    def __str__(self) -> str:
        return self.message  # Only return the message without the additional line



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
            raise DocbuildModelValidationError(
                (f"Invalid language code '{value}'. "
                 f"Expected one of {', '.join(sorted(cls.ALLOWED_LANGS))}"),
                code=None
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
