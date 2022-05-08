#!/bin/sh

tests() {
    poetry run pytest -v -s --asyncio-mode=strict
    poetry run npx pyright ./
    poetry run flake8
}

if ! [ command -v poetry &> /dev/null ]; then
   tests
else
    echo "Poetry not setup."
    exit
fi
