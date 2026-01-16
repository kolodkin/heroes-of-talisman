"""
Tests for Character Select Stage Actions.

These tests verify character selection behavior including highlighting
selected characters and confirming selections to transition to battle.
"""

import pytest

from server.game_engine import GameEngine
from ..models import (
    GamePlay,
    Player,
    CharacterCard,
    ActivePlayer1,
    ActivePlayer2,
    GameException,
    ReportedException,
    SkipTurnEffect,
    CHARACTER_DEFAULT_STATS,
    CHARACTER_SELECT,
    CHARACTER_PRESS,
    CHARACTER_SELECT_ACTION,
    ABILITY_SELECTION,
    BATTLE_DICE_ROLL,
    KNIGHT,
    ARCHER,
    MAGE,
    FREEZE,
    BATTLE_HOWL,
    init_characters,
)


def test_character_press_action_valid():
    """Test pressing a character highlights it in stage_meta"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(CHARACTER_PRESS, character=KNIGHT)

    assert game.stage_meta is not None
    assert game.stage_meta.selected == KNIGHT
    assert game.stage == CHARACTER_SELECT  # Still in character select


def test_character_press_action_not_active_player():
    """Test pressing character when not active player raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    engine = GameEngine("test_game", "player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        engine.run_action(CHARACTER_PRESS, character=KNIGHT)


def test_character_press_action_wrong_stage():
    """Test pressing character in wrong stage raises error"""
    game = GamePlay(stage=BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        engine.run_action(CHARACTER_PRESS, character=KNIGHT)


def test_character_press_action_invalid_character():
    """Test pressing non-existent character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters={})

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="not available"):
        engine.run_action(CHARACTER_PRESS, character=KNIGHT)


def test_character_select_action_valid():
    """Test confirming character selection transitions to ability_selection"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(CHARACTER_SELECT_ACTION, character=KNIGHT)

    assert game.active.player == "player1"
    assert game.active.character == KNIGHT
    assert isinstance(game.active, ActivePlayer2)
    assert game.stage == ABILITY_SELECTION
    # Knight has only one ability, so it should be auto-selected
    assert game.stage_meta is not None
    assert game.stage_meta.selected == BATTLE_HOWL


def test_character_select_action_not_active_player():
    """Test confirming selection when not active player raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    engine = GameEngine("test_game", "player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        engine.run_action(CHARACTER_SELECT_ACTION, character=KNIGHT)


def test_character_select_action_wrong_stage():
    """Test confirming selection in wrong stage raises error"""
    game = GamePlay(stage=BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        engine.run_action(CHARACTER_SELECT_ACTION, character=KNIGHT)


def test_character_select_action_invalid_character():
    """Test confirming non-existent character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters={})

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="not available"):
        engine.run_action(CHARACTER_SELECT_ACTION, character=KNIGHT)


def test_character_press_action_dead_character():
    """Test pressing a dead character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    # Kill the knight
    characters[KNIGHT].health = 0
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        engine.run_action(CHARACTER_PRESS, character=KNIGHT)


def test_character_select_action_dead_character():
    """Test confirming selection of a dead character raises error"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    # Kill the knight
    characters[KNIGHT].health = 0
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        engine.run_action(CHARACTER_SELECT_ACTION, character=KNIGHT)


def test_character_select_action_removes_skip_turn_effects():
    """Test that character selection removes all SkipTurnEffects from active player's characters"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # Add SkipTurnEffect to knight (can't be selected this turn)
    characters[KNIGHT].effects.append(SkipTurnEffect(source=FREEZE))
    # Add SkipTurnEffect to archer too
    characters[ARCHER].effects.append(SkipTurnEffect(source=FREEZE))

    game.players["player1"] = Player(name="player1", characters=characters)

    # Player selects mage (the only character without skip_turn)
    engine = GameEngine("test_game", "player1", game)
    engine.run_action(CHARACTER_SELECT_ACTION, character=MAGE)

    # Verify skip turn effects were removed from both knight and archer
    assert len(game.players["player1"].characters[KNIGHT].effects) == 0
    assert len(game.players["player1"].characters[ARCHER].effects) == 0
    # Mage should still have no effects
    assert len(game.players["player1"].characters[MAGE].effects) == 0


def test_character_select_action_removes_all_skip_turn_effects():
    """Test that all SkipTurnEffects are removed (not just the first one)"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # Add two SkipTurnEffects to knight
    characters[KNIGHT].effects.append(SkipTurnEffect(source=FREEZE))
    characters[KNIGHT].effects.append(SkipTurnEffect(source=FREEZE))

    game.players["player1"] = Player(name="player1", characters=characters)

    # Player selects mage
    engine = GameEngine("test_game", "player1", game)
    engine.run_action(CHARACTER_SELECT_ACTION, character=MAGE)

    # Verify all skip turn effects were removed
    knight_effects = game.players["player1"].characters[KNIGHT].effects
    assert len(knight_effects) == 0
