#!/bin/sh

tests() {
    poetry run pytest
    poetry run mypy ./ --strict --implicit-reexport --show-error-codes
    poetry run flake8
}

if ! [ command -v poetry &> /dev/null ]; then
   tests
else
    echo "Poetry not setup."
    exit
fi
