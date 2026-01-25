"""
Tests for Sacred Sword Card.

Sacred Sword provides +3 attack bonus but is restricted from archers.
"""

import pytest

from ..stage_card_draw import CardSelectAction
from ...common import CHARACTER_KNIGHT, CHARACTER_MAGE, CHARACTER_ARCHER
from ...cards import CARD_SACRED_SWORD
from ...effects import AttackBonusEffect
from ...gameplay import (
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    GamePlay,
    Player,
    ActivePlayer2,
    CardDrawMeta,
    init_characters,
)
from ...presets import get_debug_preset, PRESET_CARD_DRAW_ARCHER_SACRED_SWORD


def test_sacred_sword_applies_attack_bonus():
    """Test sacred_sword applies +3 attack bonus to knight"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_SACRED_SWORD

    # Check character has attack bonus effect
    player = updated_game.players["player1"]
    knight = player.characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], AttackBonusEffect)
    assert knight.effects[0].attack_bonus == 3
    assert knight.effects[0].source == CARD_SACRED_SWORD
    assert knight.effects[0].dispose_actions == []

    # Check card added to character's card list
    assert CARD_SACRED_SWORD in knight.cards


def test_sacred_sword_rejected_by_archer():
    """Test sacred_sword is not added when archer tries to use it"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_ARCHER),
        stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state transitions correctly
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_SACRED_SWORD

    # Verify archer doesn't have the effect (restricted character)
    player = updated_game.players["player1"]
    archer = player.characters[CHARACTER_ARCHER]
    assert len(archer.effects) == 0

    # Card should NOT be added to character's card list (restricted character)
    assert CARD_SACRED_SWORD not in archer.cards


def test_sacred_sword_works_for_mage():
    """Test sacred_sword works fine for mage"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_SACRED_SWORD

    # Check mage has attack bonus effect
    player = updated_game.players["player1"]
    mage = player.characters[CHARACTER_MAGE]
    assert len(mage.effects) == 1
    assert isinstance(mage.effects[0], AttackBonusEffect)
    assert mage.effects[0].attack_bonus == 3


def test_sacred_sword_archer_restriction_from_preset():
    """Test archer sacred_sword restriction using the preset"""
    game = get_debug_preset(PRESET_CARD_DRAW_ARCHER_SACRED_SWORD)

    # Verify preset is set up correctly
    assert game.stage == STAGE_CARD_DRAW
    assert game.active.character == CHARACTER_ARCHER
    assert game.stage_meta.drawn_card == CARD_SACRED_SWORD

    # Execute card selection
    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Verify restriction behavior
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    player = updated_game.players["player1"]
    archer = player.characters[CHARACTER_ARCHER]

    # Archer should not have the effect
    assert len(archer.effects) == 0

    # Card should not be added to archer's card list
    assert CARD_SACRED_SWORD not in archer.cards
