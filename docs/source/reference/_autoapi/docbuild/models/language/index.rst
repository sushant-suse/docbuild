docbuild.models.language
========================

.. py:module:: docbuild.models.language

.. autoapi-nested-parse::

   Language model for representing language codes.



Classes
-------

.. autoapisummary::

   docbuild.models.language.LanguageCode


Module Contents
---------------

.. py:class:: LanguageCode(language: str, **kwargs: dict[Any, Any])

   Bases: :py:obj:`pydantic.BaseModel`


   The language in the format language-country (all lowercase).

   It accepts also an underscore as a separator instead of a dash.
   Use "*" to denote "ALL" languages


   .. py:attribute:: language
      :type:  str
      :value: None


      The natural language in the format ll-cc, where 'll' is the language and 'cc' the country.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary
      conforming to Pydantic's :class:`~pydantic.config.ConfigDict`.



   .. py:attribute:: ALLOWED_LANGS
      :type:  ClassVar[frozenset]

      Class variable containing all allowed languages.



   .. py:method:: matches(other: LanguageCode | str) -> bool

      Return True if this LanguageCode matches the other, considering wildcards.

      The string '*' matches any language:

      >>> LanguageCode("*").matches("de-de")
      True
      >>> LanguageCode("de-de").matches("*")
      True



   .. py:method:: validate_language(value: str) -> str
      :classmethod:


      Check if the passed language adheres to the allowed language.



   .. py:method:: lang() -> str

      Extract the language part of the language code (property).



   .. py:method:: country() -> str

      Extract the country part of the language code (property).



