"""Configuration module for the scheduler application."""
import json
import os

# Path to benchmarks JSON file
BENCHMARKS_PATH = os.path.join(os.path.dirname(__file__), 'benchmarks', 'benchmarks.json')

# Load benchmarks data
with open(BENCHMARKS_PATH, 'r') as f:
    BENCHMARKS = json.load(f)

