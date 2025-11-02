"""
Tests for Character Select Stage Actions.

These tests verify character selection behavior including highlighting
selected characters and confirming selections to transition to battle.
"""

import pytest

from .stage_character_select import CharacterPressAction, CharacterSelectAction
from ..models import (
    GamePlay,
    Player,
    CharacterCard,
    ActivePlayer1,
    ActivePlayer2,
    GameException,
    ReportedException,
    CHARACTER_DEFAULT_STATS,
    CHARACTER_SELECT,
    ABILITY_SELECTION,
    BATTLE_DICE_ROLL,
    KNIGHT,
    ARCHER,
    MAGE,
    init_characters,
)


def test_character_press_action_valid():
    """Test pressing a character highlights it in stage_meta"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)
    updated_game = action.run(character=KNIGHT)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == KNIGHT
    assert updated_game.stage == CHARACTER_SELECT  # Still in character select


def test_character_press_action_not_active_player():
    """Test pressing character when not active player raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = CharacterPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(character=KNIGHT)


def test_character_press_action_wrong_stage():
    """Test pressing character in wrong stage raises error"""
    game = GamePlay(stage=BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot select character in stage"):
        action.run(character=KNIGHT)


def test_character_press_action_invalid_character():
    """Test pressing non-existent character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters={})

    action = CharacterPressAction("player1", game)

    with pytest.raises(ReportedException, match="not available"):
        action.run(character=KNIGHT)


def test_character_select_action_valid():
    """Test confirming character selection transitions to ability_selection"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(character=KNIGHT)

    assert updated_game.active.player == "player1"
    assert updated_game.active.character == KNIGHT
    assert isinstance(updated_game.active, ActivePlayer2)
    assert updated_game.stage == ABILITY_SELECTION
    assert updated_game.stage_meta is None  # Cleared after transition


def test_character_select_action_not_active_player():
    """Test confirming selection when not active player raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = CharacterSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(character=KNIGHT)


def test_character_select_action_wrong_stage():
    """Test confirming selection in wrong stage raises error"""
    game = GamePlay(stage=BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot confirm selection in stage"):
        action.run(character=KNIGHT)


def test_character_select_action_invalid_character():
    """Test confirming non-existent character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters={})

    action = CharacterSelectAction("player1", game)

    with pytest.raises(ReportedException, match="not available"):
        action.run(character=KNIGHT)


def test_character_press_action_dead_character():
    """Test pressing a dead character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    # Kill the knight
    characters[KNIGHT].health = 0
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        action.run(character=KNIGHT)


def test_character_select_action_dead_character():
    """Test confirming selection of a dead character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    # Kill the knight
    characters[KNIGHT].health = 0
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        action.run(character=KNIGHT)


def test_character_press_action_skip_next_turn():
    """Test pressing a character with skip_next_turn effect raises error"""
    from ..models import SkipTurnEffect, FREEZE

    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    # Add skip turn effect to knight
    characters[KNIGHT].effects = [SkipTurnEffect(source=FREEZE)]
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)

    with pytest.raises(ReportedException, match="must skip this turn"):
        action.run(character=KNIGHT)


def test_character_select_action_skip_next_turn():
    """Test confirming selection of a character with skip_next_turn effect raises error"""
    from ..models import SkipTurnEffect, FREEZE

    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    # Add skip turn effect to knight
    characters[KNIGHT].effects = [SkipTurnEffect(source=FREEZE)]
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)

    with pytest.raises(ReportedException, match="must skip this turn"):
        action.run(character=KNIGHT)
