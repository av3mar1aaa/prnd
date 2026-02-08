#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Добавляем родительскую папку (…/Downloads) в sys.path,
# чтобы импорт prnd.settings работал.
BASE_DIR = Path(__file__).resolve().parent          # …/Downloads/prnd
PROJECT_ROOT = BASE_DIR.parent                      # …/Downloads
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prnd.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

