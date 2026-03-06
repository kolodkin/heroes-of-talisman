"""
Tests for GamePlay models.

These tests verify model behavior including computed properties.
"""

from .common import CHARACTER_KNIGHT
from .abilities import ABILITIES_MAP, ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE
from .effects import APPLY_TO_SELECTED_OPPONENT
from .gameplay import init_characters, KNIGHT_L1_DEFAULT_HEALTH


def test_character_is_alive_when_health_positive():
    """Test character is alive when health > 0"""
    characters = init_characters()
    assert characters[CHARACTER_KNIGHT].health == KNIGHT_L1_DEFAULT_HEALTH
    assert characters[CHARACTER_KNIGHT].is_alive is True


def test_ability_apply_to_selected_opponent():
    """Test which abilities target a selected opponent (only FREEZE with SkipTurnEffect)"""
    # Only ABILITY_FREEZE targets a selected opponent (has SkipTurnEffect)
    freeze_effects = ABILITIES_MAP[ABILITY_FREEZE].effects
    assert any(e.apply_to == APPLY_TO_SELECTED_OPPONENT for e in freeze_effects)

    # Other abilities don't require opponent selection
    howl_effects = ABILITIES_MAP[ABILITY_BATTLE_HOWL].effects
    assert not any(e.apply_to == APPLY_TO_SELECTED_OPPONENT for e in howl_effects)

    arrow_effects = ABILITIES_MAP[ABILITY_BOUNCING_ARROW].effects
    assert not any(e.apply_to == APPLY_TO_SELECTED_OPPONENT for e in arrow_effects)
