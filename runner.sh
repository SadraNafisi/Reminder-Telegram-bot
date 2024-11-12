#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

echo "today is $(date)"
source "$SCRIPT_DIR/.venv/bin/activate"
python "$SCRIPT_DIR/database.py"
python "$SCRIPT_DIR/telegram_bot.py"