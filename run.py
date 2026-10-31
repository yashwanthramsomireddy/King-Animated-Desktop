"""Entry point:  python run.py [--settings] [--background]"""
import sys
from king_pets.engine import run

if __name__ == "__main__":
    sys.exit(run(open_settings="--settings" in sys.argv, background="--background" in sys.argv))
