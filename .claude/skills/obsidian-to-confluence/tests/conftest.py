"""
Pytest configuration - adds the scripts directory to sys.path so test
modules can import md_to_adf, review_table_adf, and annotate_adf directly.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
