"""Language model for representing language codes."""

from functools import total_ordering
import re
from typing import Annotated, Any, ClassVar

from pydantic import BaseModel, Field, computed_field
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

@total_ordering
class LanguageCode(BaseModel):
    """The language in the format language-country (all lowercase).

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
        {"*"} | ALLOWED_LANGUAGES,
    )

    def __init__(self, language: str, **kwargs: dict[Any, Any]) -> None:
        super().__init__(language=language.replace("_", "-"), **kwargs)
        if language == "*":
            self._lang, self._country = ("*", "*")
        else:
            self._lang, self._country = re.split(r"[_-]", language)

    def __str__(self) -> str:
        """Implement str(self)."""
        return f"{self.language}"

    def __repr__(self) -> str:
        """Implement repr(self)."""
        return f"{self.__class__.__name__}(language={str(self)!r})"

    def __eq__(self, other: "object|str|LanguageCode") -> bool:
        """Implement self == other.

        The comparison does NOT break the principle of equality:
        * Reflexive: a == b
        * Symmetric: a == b <=> b == a
        * Transitive: if a == b and b == c, then a == c

        If you need to check for wildcar logic, use matches()
        """
        if isinstance(other, LanguageCode):
            return self.language == other.language
        elif isinstance(other, str):
            return self.language == other
        return NotImplemented

    def __lt__(self, other: "object|str|LanguageCode") -> bool:
        """Implement self < other.

        Special properties:
        - "*" is always the "smallest" language
        - If self contains "*" and the other not, return True
        - If self and the other contains "*", return False
        """
        if isinstance(other, LanguageCode):
            other_value = other.language
        elif isinstance(other, str):
            other_value = other
        else:
            return NotImplemented

        # "*" is always smallest
        if self.language == "*":
            return other_value != "*"
        if other_value == "*":
            return False

        # Perform string comparison after handling the wildcard case
        return self.language < other_value

    def __hash__(self) -> int:
        """Implement hash(self).

        For using 'in sets' or as dict keys
        """
        return hash(self.language)

    def matches(self, other: "LanguageCode | str") -> bool:
        """Return True if this LanguageCode matches the other, considering wildcards.

        '*' matches any language

        >>> LanguageCode("*").matches("de-de")
        True
        >>> LanguageCode("de-de").matches("*")
        True
        """
        other_value = str(other)
        return (self.language == "*" or
                other_value == "*" or
                self.language == other_value)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        """Check if the passed language adheres to the allowed language."""
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
        examples=["en", "de", "ja"],
    )
    def lang(self) -> str:
        """Extract the language part of the language code (property)."""
        return self._lang

    @computed_field(
        repr=False,
        title="The country part of the language code",
        examples=["us", "de", "jp"],
    )
    def country(self) -> str:
        """Extract the country part of the language code (property)."""
        return self._country
