"""
Tests for Metal Armor Card.

Metal Armor provides +2 defense bonus that persists across battles.
"""

import pytest

from ..stage_card_draw import CardSelectAction
from ..battle_end import BattleEndAction
from ...common import CHARACTER_KNIGHT
from ...cards import CARD_METAL_ARMOR
from ...effects import DefenseBonusEffect
from ...gameplay import (
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    GamePlay,
    Player,
    ActivePlayer2,
    CardDrawMeta,
    init_characters,
)
from ...presets import get_debug_preset, PRESET_BATTLE_METAL_ARMOR


def test_metal_armor_applies_defense_bonus():
    """Test metal_armor applies +2 defense bonus to character"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_METAL_ARMOR
    assert updated_game.stage_meta is not None  # Auto-selected ability

    # Check character has defense effect
    player = updated_game.players["player1"]
    knight = player.characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], DefenseBonusEffect)
    assert knight.effects[0].defense_bonus == 2
    assert knight.effects[0].source == CARD_METAL_ARMOR
    assert knight.effects[0].dispose_actions == []  # Persistent effect

    # Check card added to character's card list
    assert CARD_METAL_ARMOR in knight.cards


def test_metal_armor_defense_persists():
    """Test metal_armor defense effect persists across battles using preset"""
    # Get preset with knight having metal_armor and losing battle
    game = get_debug_preset(PRESET_BATTLE_METAL_ARMOR, player1_name="player1", player2_name="player2")

    # Knight should have defense effect before battle ends
    player1 = game.players["player1"]
    knight = player1.characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], DefenseBonusEffect)
    assert knight.effects[0].defense_bonus == 2

    # Knight's initial health
    knight_health_before = knight.health

    # End battle (knight loses but has +2 defense)
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Knight should take 0 damage (1 - 2 defense = 0)
    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_after.health == knight_health_before  # No damage taken

    # Defense effect should still be present (persistent, not disposed)
    assert len(knight_after.effects) == 1
    assert isinstance(knight_after.effects[0], DefenseBonusEffect)
    assert knight_after.effects[0].defense_bonus == 2
