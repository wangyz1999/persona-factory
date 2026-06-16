"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from persona_factory.factory import PersonaFactory


@pytest.fixture
def factory() -> PersonaFactory:
    return PersonaFactory(locale="en_US", seed=12345)
