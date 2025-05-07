import pytest
from pydantic import ValidationError

from docbuild.models.language import LanguageCode
from docbuild.constants import ALLOWED_LANGUAGES


@pytest.mark.parametrize("language", ALLOWED_LANGUAGES)
def test_valid_language(language):
    lang, country = language.split("-")
    thelang = LanguageCode(language=language)
    assert thelang.language == language
    assert thelang.lang == lang
    assert thelang.country == country


def test_wildcard_language():
    thelang = LanguageCode("*")
    assert thelang.language == "*"
    assert thelang.lang == "*"
    assert thelang.country == "*"


def test_unknown_language():
    with pytest.raises(ValidationError) as exc:
        LanguageCode("de-ch")
    assert "validation error" in str(exc.value)


def test_language_with_underscore():
    thelang = LanguageCode("de_de")
    assert thelang.language == "de-de"
    assert thelang.lang == "de"
    assert thelang.country == "de"
