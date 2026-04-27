"""Tests for the offline route-history evaluation script.

These tests cover script-level wrapper behavior only. They should not re-test
the shared route evaluator or network loader in detail.
"""

import json
from pathlib import Path

import pytest


def test_evaluate_history_script_can_be_imported():
    import scripts.evaluate_history

    assert scripts.evaluate_history is not None
