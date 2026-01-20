"""
Tests for Card Draw Stage Actions.

These tests verify card draw behavior including drawing a random card
and applying card effects to the character.
"""

import pytest

from .stage_card_draw import CardDrawAction, CardSelectAction
from ..common import GameException, ReportedException, KNIGHT, MAGE, ARCHER
from ..cards import METAL_ARMOR, SACRED_SWORD, CARDS_MAP
from ..effects import DefenseBonusEffect, AttackBonusEffect
from ..gameplay import (
    CARD_DRAW,
    ABILITY_SELECTION,
    CHARACTER_SELECT,
    GamePlay,
    Player,
    ActivePlayer2,
    CardDrawMeta,
    init_characters,
)


def test_card_draw_action_valid():
    """Test drawing a card stores it in stage_meta"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardDrawAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage_meta is not None
    assert isinstance(updated_game.stage_meta, CardDrawMeta)
    assert updated_game.stage_meta.drawn_card in CARDS_MAP
    assert updated_game.stage == CARD_DRAW  # Still in card draw stage


def test_card_draw_action_not_active_player():
    """Test drawing card when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = CardDrawAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_card_draw_action_wrong_stage():
    """Test drawing card in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardDrawAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_card_select_action_applies_effects():
    """Test selecting a card applies its effects to the character"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == ABILITY_SELECTION
    assert updated_game.card == METAL_ARMOR
    assert updated_game.stage_meta is not None  # Auto-selected ability

    # Check character has defense effect
    player = updated_game.players["player1"]
    knight = player.characters[KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], DefenseBonusEffect)
    assert knight.effects[0].defense_bonus == 2
    assert knight.effects[0].source == METAL_ARMOR
    assert knight.effects[0].dispose_actions == []  # Persistent effect

    # Check card added to character's card list
    assert METAL_ARMOR in knight.cards


def test_card_select_action_not_active_player():
    """Test selecting card when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=METAL_ARMOR),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = CardSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_card_select_action_no_card_drawn():
    """Test selecting card when no card was drawn raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)

    with pytest.raises(GameException, match="No card was drawn"):
        action.run()


def test_card_select_action_wrong_stage():
    """Test selecting card in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_metal_armor_defense_persists():
    """Test metal_armor defense effect persists across battles using preset"""
    from ..presets import get_debug_preset, BATTLE_METAL_ARMOR
    from .battle_end import BattleEndAction

    # Get preset with knight having metal_armor and losing battle
    game = get_debug_preset(BATTLE_METAL_ARMOR, player1_name="player1", player2_name="player2")

    # Knight should have defense effect before battle ends
    player1 = game.players["player1"]
    knight = player1.characters[KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], DefenseBonusEffect)
    assert knight.effects[0].defense_bonus == 2

    # Knight's initial health
    knight_health_before = knight.health

    # End battle (knight loses but has +2 defense)
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Knight should take 0 damage (1 - 2 defense = 0)
    knight_after = updated_game.players["player1"].characters[KNIGHT]
    assert knight_after.health == knight_health_before  # No damage taken

    # Defense effect should still be present (persistent, not disposed)
    assert len(knight_after.effects) == 1
    assert isinstance(knight_after.effects[0], DefenseBonusEffect)
    assert knight_after.effects[0].defense_bonus == 2


def test_sacred_sword_applies_attack_bonus():
    """Test sacred_sword applies +3 attack bonus to knight"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == ABILITY_SELECTION
    assert updated_game.card == SACRED_SWORD

    # Check character has attack bonus effect
    player = updated_game.players["player1"]
    knight = player.characters[KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], AttackBonusEffect)
    assert knight.effects[0].attack_bonus == 3
    assert knight.effects[0].source == SACRED_SWORD
    assert knight.effects[0].dispose_actions == []

    # Check card added to character's card list
    assert SACRED_SWORD in knight.cards


def test_sacred_sword_rejected_by_archer():
    """Test sacred_sword is not added when archer tries to use it"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=ARCHER),
        stage_meta=CardDrawMeta(drawn_card=SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state transitions correctly
    assert updated_game.stage == ABILITY_SELECTION
    assert updated_game.card == SACRED_SWORD

    # Verify archer doesn't have the effect (restricted character)
    player = updated_game.players["player1"]
    archer = player.characters[ARCHER]
    assert len(archer.effects) == 0

    # Card should NOT be added to character's card list (restricted character)
    assert SACRED_SWORD not in archer.cards


def test_sacred_sword_works_for_mage():
    """Test sacred_sword works fine for mage"""
    characters = init_characters()
    game = GamePlay(
        stage=CARD_DRAW,
        active=ActivePlayer2(player="player1", character=MAGE),
        stage_meta=CardDrawMeta(drawn_card=SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == ABILITY_SELECTION
    assert updated_game.card == SACRED_SWORD

    # Check mage has attack bonus effect
    player = updated_game.players["player1"]
    mage = player.characters[MAGE]
    assert len(mage.effects) == 1
    assert isinstance(mage.effects[0], AttackBonusEffect)
    assert mage.effects[0].attack_bonus == 3
