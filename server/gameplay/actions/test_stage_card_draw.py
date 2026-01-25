"""
Tests for Card Draw Stage Actions.

These tests verify card draw behavior including drawing a random card
and applying card effects to the character.

Card-specific tests are in the e2e/ folder:
- test_card_metal_armor.py
- test_card_sacred_sword.py
- test_card_golden_apple.py
"""

import pytest

from .stage_card_draw import CardDrawAction, CardSelectAction
from ..common import GameException, ReportedException, CHARACTER_KNIGHT
from ..cards import CARD_METAL_ARMOR, CARDS_MAP
from ..gameplay import (
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    STAGE_CHARACTER_SELECT,
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
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardDrawAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage_meta is not None
    assert isinstance(updated_game.stage_meta, CardDrawMeta)
    assert updated_game.stage_meta.drawn_card in CARDS_MAP
    assert updated_game.stage == STAGE_CARD_DRAW  # Still in card draw stage


def test_card_draw_action_not_active_player():
    """Test drawing card when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
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
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardDrawAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_card_select_action_transitions_stage():
    """Test selecting a card transitions to ability selection stage"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state transitions
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_METAL_ARMOR
    assert updated_game.stage_meta is not None  # Auto-selected ability


def test_card_select_action_not_active_player():
    """Test selecting card when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
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
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)

    with pytest.raises(GameException, match="No card was drawn"):
        action.run()


def test_card_select_action_wrong_stage():
    """Test selecting card in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()
