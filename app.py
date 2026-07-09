import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ["MODE"] = "live"

from orquestador import main

if __name__ == "__main__":
    main()