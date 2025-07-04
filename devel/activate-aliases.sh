#!/bin/bash

# For testing:
alias upytest="uv run --frozen pytest"

# For executing the project's script:
alias docbuild="uv run --frozen docbuild"

# For managing changelog and news files:
alias towncrier="uv run --frozen towncrier"

# For creating docs:
alias makedocs="uv run --frozen make -C docs html"
