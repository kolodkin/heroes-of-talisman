"""
Tests for Golden Apple Card.

Golden Apple heals +1 health instantly, capped at max_health.
"""

import pytest

from .stage_card_draw import CardSelectAction
from ..common import CHARACTER_KNIGHT
from ..cards import CARD_GOLDEN_APPLE
from ..gameplay import STAGE_CARD_DRAW
from ..presets import (
    get_debug_preset,
    PRESET_CARD_DRAW_KNIGHT_GOLDEN_APPLE,
    PRESET_CARD_DRAW_GOLDEN_APPLE_MAX_HEALTH,
)


def test_golden_apple_heals_damaged_knight():
    """Test golden_apple heals knight from 1 to 2 health using preset"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_GOLDEN_APPLE)

    # Verify preset: knight at 1 health
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.health == 1

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check knight healed to 2
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.health == 2
    assert CARD_GOLDEN_APPLE in knight.cards


def test_golden_apple_does_not_exceed_max_health():
    """Test golden_apple healing is capped at max_health using preset"""
    game = get_debug_preset(PRESET_CARD_DRAW_GOLDEN_APPLE_MAX_HEALTH)

    # Verify preset: knight at max health (2/2)
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.health == knight_before.max_health

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check character health doesn't exceed max
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.health == 2  # Still at max, not 3
    assert knight.health <= knight.max_health
    assert CARD_GOLDEN_APPLE in knight.cards
