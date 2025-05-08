import pytest
from pydantic import ValidationError

from docbuild.models.language import LanguageCode
from docbuild.constants import ALLOWED_LANGUAGES


@pytest.mark.parametrize("language", sorted(ALLOWED_LANGUAGES))
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


def test_str_in_language():
    thelang = LanguageCode("de_de")
    assert str(thelang) == "de-de"

def test_repr_in_language():
    thelang = LanguageCode("de-de")
    assert repr(thelang) == "LanguageCode(language='de-de')"


def test_compare_two_uneqal_languages():
    lang1 = LanguageCode("en-us")
    lang2 = LanguageCode("de-de")
    assert lang1 != lang2
    assert lang2 != lang1


def test_compare_two_eqal_languages():
    lang1 = LanguageCode("de-de")
    lang2 = LanguageCode("de-de")
    assert lang1 == lang2
    assert lang2 == lang1


def test_compare_with_all_language():
    lang1 = LanguageCode("*")
    lang2 = LanguageCode("de-de")
    assert lang1 == lang2
    assert lang2 == lang1


def test_compare_with_one_language_and_with_different_object():
    lang1 = LanguageCode("*")
    lang2 = object()
    assert lang1 != lang2


def test_language_code_is_frozen():
    lang = LanguageCode(language="en-us")

    with pytest.raises(ValidationError, match=".*frozen_instance.*"):
        lang.language = "de-de"


def test_language_code_is_hashable():
    lang = LanguageCode(language="en-us")
    s = { lang }  # Should not raise TypeError
    assert lang in s

def test_compare_languagecode_with_str():
    lang1 = LanguageCode("de-de")
    lang2 = "de-de"
    assert lang1 == lang2
    assert lang2 == lang1