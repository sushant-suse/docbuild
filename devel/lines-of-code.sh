#!/bin/sh
#
# Other tools
# - tokei
# - sloccount
# - loc
# - ohcount

# cloc --exclude-dir=.venv,.ruff_cache,.pytest_cache,.git,contrib,docs .

tokei $@
