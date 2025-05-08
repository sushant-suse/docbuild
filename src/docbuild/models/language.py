import re
from typing import Annotated, ClassVar

from pydantic import BaseModel, computed_field, Field
from pydantic.config import ConfigDict
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

    language: Annotated[str, Field(
        title="The natural language",
        description=(
            "A natural language in the format ll-cc, "
            "whereas 'll' is the language and 'cc' the country "
            "both in lowercase letters. "
            "The special syntax '*' denotes every language."
            ),
        examples=["en-us", "de-de"],
        frozen=True,
    )]

    model_config = ConfigDict(frozen=True)

    ALLOWED_LANGS: ClassVar[frozenset] = frozenset(
        {"*"} | ALLOWED_LANGUAGES
    )

    def __init__(self, language, **kwargs):
        super().__init__(language=language.replace("_", "-"), **kwargs)
        if language == "*":
            self._lang, self._country = ("*", "*")
        else:
            self._lang, self._country = re.split(r"[_-]", language)

    def __str__(self):
        """Implement str(self)"""
        return f"{self.language}"

    def __repr__(self):
        """Implement repr(self)"""
        return f"{self.__class__.__name__}(language={str(self)!r})"

    def __eq__(self, other: "object|str|LanguageCode") -> bool:
        """Implement self == other"""
        if not isinstance(other, (LanguageCode, str)):
            return NotImplemented

        if isinstance(other, str):
            return "*" in other or (self.language == other)

        if "*" in (self.lang, other.lang):
            # Comparing an "ALL" language with other should be treated as True
            return True
        return (self.lang, self.country) == (other.lang, other.country)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value):
        """Check if the passed language adheres to the allowed language"""
        # value = value.replace("_", "-")
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
