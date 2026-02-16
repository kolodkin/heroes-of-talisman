"""
Tests for GamePlay models.

These tests verify model behavior including computed properties.
"""

from .common import CHARACTER_KNIGHT
from .abilities import ABILITIES_MAP, ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE
from .gameplay import init_characters, KNIGHT_L1_DEFAULT_HEALTH


def test_character_is_alive_when_health_positive():
    """Test character is alive when health > 0"""
    characters = init_characters()
    assert characters[CHARACTER_KNIGHT].health == KNIGHT_L1_DEFAULT_HEALTH
    assert characters[CHARACTER_KNIGHT].is_alive is True


def test_ability_requires_opponent_selection():
    """Test which abilities require opponent selection (only FREEZE with SkipTurnEffect)"""
    # Only ABILITY_FREEZE requires opponent selection (has SkipTurnEffect)
    assert ABILITIES_MAP[ABILITY_FREEZE].requires_opponent_selection is True

    # Other abilities are applied to battle opponent automatically
    assert ABILITIES_MAP[ABILITY_BATTLE_HOWL].requires_opponent_selection is False
    assert ABILITIES_MAP[ABILITY_BOUNCING_ARROW].requires_opponent_selection is False
