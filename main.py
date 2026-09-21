"""
main.py - Root entry point for BlackoutMode application.
"""

import sys
import os

# Add src to sys.path
here = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(here, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from blackout.app import main

if __name__ == "__main__":
    main()
