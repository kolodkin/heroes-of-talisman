"""
Tests for Character Select Stage Actions.

These tests verify character selection behavior including highlighting
selected characters and confirming selections to transition to battle.
"""

import pytest

from .stage_character_select import CharacterPressAction, CharacterSelectAction
from ..models import (
    GameException,
    ReportedException,
    KNIGHT,
    ARCHER,
    MAGE,
)
from ..abilities import FREEZE, BATTLE_HOWL
from ..effects import SkipTurnEffect
from ..gameplay import (
    CHARACTER_SELECT,
    ABILITY_SELECTION,
    BATTLE_DICE_ROLL,
    GamePlay,
    Player,
    Character,
    ActivePlayer1,
    ActivePlayer2,
    CHARACTER_DEFAULT_STATS,
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

    with pytest.raises(GameException, match="Cannot perform action in stage"):
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
    # Knight has only one ability, so it should be auto-selected
    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == BATTLE_HOWL


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

    with pytest.raises(GameException, match="Cannot perform action in stage"):
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
    action = CharacterSelectAction("player1", game)
    updated_game = action.run(character=MAGE)

    # Verify skip turn effects were removed from both knight and archer
    assert len(updated_game.players["player1"].characters[KNIGHT].effects) == 0
    assert len(updated_game.players["player1"].characters[ARCHER].effects) == 0
    # Mage should still have no effects
    assert len(updated_game.players["player1"].characters[MAGE].effects) == 0


def test_character_select_action_removes_all_skip_turn_effects():
    """Test that all SkipTurnEffects are removed (not just the first one)"""
    game = GamePlay(stage=CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # Add two SkipTurnEffects to knight
    characters[KNIGHT].effects.append(SkipTurnEffect(source=FREEZE))
    characters[KNIGHT].effects.append(SkipTurnEffect(source=FREEZE))

    game.players["player1"] = Player(name="player1", characters=characters)

    # Player selects mage
    action = CharacterSelectAction("player1", game)
    updated_game = action.run(character=MAGE)

    # Verify all skip turn effects were removed
    knight_effects = updated_game.players["player1"].characters[KNIGHT].effects
    assert len(knight_effects) == 0
