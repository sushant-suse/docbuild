# Ideas

This is a unsorted collection of ideas what could be implemented.

* Doctypes and language.
  The language type allows en-us, de-de, and the asterisk to match
  "all" languages. However, we don't have an expressive value that
  matches "all languages except English".
  Maybe allow "-" in front of the language?
  * "-en-us" would match all languages minus English.
  * "-en-us,-de-de" would match all languages minus English and German.
    Should the second dash be optional?
