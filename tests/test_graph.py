import pytest
from unittest.mock import patch, MagicMock
from app.graph.graph import should_revise


def test_should_revise_returns_approved():
    state = {"critic_approved": True}
    assert should_revise(state) == "approved"


def test_should_revise_returns_revise():
    state = {"critic_approved": False}
    assert should_revise(state) == "revise"


def test_should_revise_defaults_to_revise():
    state = {}
    assert should_revise(state) == "revise"