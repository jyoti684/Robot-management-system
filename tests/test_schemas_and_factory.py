from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import MoveCommand
from app.services.robot_client import RobotCommandFactory


def test_factory_creates_expected_payload():
    command = MoveCommand(direction="up", steps=2)
    assert RobotCommandFactory.create_payload(command) == {"direction": "up", "steps": 2}


def test_invalid_direction_is_rejected():
    with pytest.raises(ValidationError):
        MoveCommand(direction="diagonal", steps=1)


def test_steps_above_five_are_rejected():
    with pytest.raises(ValidationError):
        MoveCommand(direction="up", steps=6)
