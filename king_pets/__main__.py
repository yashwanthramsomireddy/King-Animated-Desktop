import sys
from .engine import run

if __name__ == "__main__":
    sys.exit(run(open_settings="--settings" in sys.argv, background="--background" in sys.argv))
