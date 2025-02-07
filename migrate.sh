#!/bin/bash

# Example usage:
# Usage: ./migrate.sh <env> "<revision desc>"
# Example: ./migrate.sh local "add users table"

ENV=$1
DESC=$2

alembic -n $ENV revision --autogenerate -m "$DESC"
alembic -n $ENV upgrade head