import sys
import os

# Add the parent directory to sys.path so tests can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
