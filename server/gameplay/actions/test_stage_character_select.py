"""
Tests for Character Select Stage Actions.

These tests verify character selection behavior including highlighting
selected characters and confirming selections to transition to battle.
"""

import pytest

from .stage_character_select import CharacterPressAction, CharacterSelectAction, SkipTurnAction
from ..common import (
    GameException,
    ReportedException,
    CHARACTER_KNIGHT,
    CHARACTER_ARCHER,
    CHARACTER_MAGE,
)
from ..effects import EFFECT_SKIP_TURN
from ..gameplay import (
    STAGE_CHARACTER_SELECT,
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    STAGE_BATTLE_DICE_ROLL,
    GamePlay,
    Player,
    ActivePlayer1,
    ActivePlayer2,
    init_characters,
)


def kill_character(characters, character_type):
    characters[character_type].health = 0
    characters[character_type].is_alive = False


def test_character_press_action_valid():
    """Test pressing a character highlights it in stage_meta"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)
    updated_game = action.run(character=CHARACTER_KNIGHT)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == CHARACTER_KNIGHT
    assert updated_game.stage == STAGE_CHARACTER_SELECT  # Still in character select


def test_character_press_action_not_active_player():
    """Test pressing character when not active player raises error"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = CharacterPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_press_action_wrong_stage():
    """Test pressing character in wrong stage raises error"""
    game = GamePlay(stage=STAGE_BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_press_action_invalid_character():
    """Test pressing non-existent character raises error"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters={})

    action = CharacterPressAction("player1", game)

    with pytest.raises(ReportedException, match="not available"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_select_action_valid():
    """Test confirming character selection transitions to card_draw"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(character=CHARACTER_KNIGHT)

    assert updated_game.active.player == "player1"
    assert updated_game.active.character == CHARACTER_KNIGHT
    assert isinstance(updated_game.active, ActivePlayer2)
    assert updated_game.stage == STAGE_CARD_DRAW
    # Stage meta should be cleared (card will be drawn in next stage)
    assert updated_game.stage_meta is None


def test_character_select_action_not_active_player():
    """Test confirming selection when not active player raises error"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = CharacterSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_select_action_wrong_stage():
    """Test confirming selection in wrong stage raises error"""
    game = GamePlay(stage=STAGE_BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_select_action_invalid_character():
    """Test confirming non-existent character raises error"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters={})

    action = CharacterSelectAction("player1", game)

    with pytest.raises(ReportedException, match="not available"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_press_action_dead_character():
    """Test pressing a dead character raises error"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    kill_character(characters, CHARACTER_KNIGHT)
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterPressAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_select_action_dead_character():
    """Test confirming selection of a dead character raises error"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()
    kill_character(characters, CHARACTER_KNIGHT)
    game.players["player1"] = Player(name="player1", characters=characters)

    action = CharacterSelectAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        action.run(character=CHARACTER_KNIGHT)


def test_character_select_action_removes_skip_turn_effects():
    """Test that character selection removes all skip_turn effects from active player's characters"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # Add skip_turn effect to knight (can't be selected this turn)
    characters[CHARACTER_KNIGHT].effects = [EFFECT_SKIP_TURN]
    # Add skip_turn effect to archer too
    characters[CHARACTER_ARCHER].effects = [EFFECT_SKIP_TURN]

    game.players["player1"] = Player(name="player1", characters=characters)

    # Player selects mage (the only character without skip_turn)
    action = CharacterSelectAction("player1", game)
    updated_game = action.run(character=CHARACTER_MAGE)

    # Verify skip turn effects were removed from both knight and archer
    assert len(updated_game.players["player1"].characters[CHARACTER_KNIGHT].effects) == 0
    assert len(updated_game.players["player1"].characters[CHARACTER_ARCHER].effects) == 0
    # Mage should still have no effects
    assert len(updated_game.players["player1"].characters[CHARACTER_MAGE].effects) == 0


def test_character_select_action_removes_all_skip_turn_effects():
    """Test that all skip_turn effects are removed (not just the first one)"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # Add two skip_turn effects to knight
    characters[CHARACTER_KNIGHT].effects = [EFFECT_SKIP_TURN, EFFECT_SKIP_TURN]

    game.players["player1"] = Player(name="player1", characters=characters)

    # Player selects mage
    action = CharacterSelectAction("player1", game)
    updated_game = action.run(character=CHARACTER_MAGE)

    # Verify all skip turn effects were removed
    knight_effects = updated_game.players["player1"].characters[CHARACTER_KNIGHT].effects
    assert len(knight_effects) == 0


def test_skip_turn_action_with_preset():
    """Test SkipTurnAction using the skip_turn_no_character preset"""
    from ..presets import get_debug_preset

    game = get_debug_preset("skip_turn_no_character")

    # Verify preset state - knight and archer dead, mage has skip turn
    p1_chars = game.players["player1"].characters
    assert p1_chars[CHARACTER_KNIGHT].health == 0
    assert p1_chars[CHARACTER_ARCHER].health == 0
    assert p1_chars[CHARACTER_MAGE].effect.skip_next_turn is True

    # Player 1 is active
    assert game.active.player == "player1"

    action = SkipTurnAction("player1", game)
    updated_game = action.run()

    # Verify turn was skipped to player2
    assert updated_game.active.player == "player2"
    assert updated_game.stage == STAGE_CHARACTER_SELECT

    # Verify skip turn effects were disposed
    assert p1_chars[CHARACTER_MAGE].effect.skip_next_turn is False
    assert len(p1_chars[CHARACTER_MAGE].effects) == 0


def test_skip_turn_action_not_active_player():
    """Test SkipTurnAction raises error when not active player"""
    from ..presets import get_debug_preset

    game = get_debug_preset("skip_turn_no_character")

    action = SkipTurnAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_skip_turn_action_with_available_character_fails():
    """Test SkipTurnAction fails if there's an available character"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # Knight and archer dead, but mage is alive and has no skip turn
    kill_character(characters, CHARACTER_KNIGHT)
    kill_character(characters, CHARACTER_ARCHER)
    # Mage is alive with no effects - should be available

    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=init_characters())

    action = SkipTurnAction("player1", game)

    with pytest.raises(ReportedException, match="Cannot skip turn: available characters exist"):
        action.run()


def test_skip_turn_action_wrong_stage():
    """Test SkipTurnAction raises error in wrong stage"""
    game = GamePlay(stage=STAGE_BATTLE_DICE_ROLL, active=ActivePlayer1(player="player1"))
    game.players["player1"] = Player(name="player1", characters=init_characters())

    action = SkipTurnAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_skip_turn_action_disposes_effects():
    """Test that SkipTurnAction disposes skip turn effects"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player1"))
    characters = init_characters()

    # No selectable characters: knight and archer are dead, mage has skip turn
    kill_character(characters, CHARACTER_KNIGHT)
    kill_character(characters, CHARACTER_ARCHER)
    characters[CHARACTER_MAGE].effects = [EFFECT_SKIP_TURN]

    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=init_characters())

    action = SkipTurnAction("player1", game)
    updated_game = action.run()

    # Verify skip turn effects were disposed from mage
    mage = updated_game.players["player1"].characters[CHARACTER_MAGE]
    assert len(mage.effects) == 0
    assert mage.effect.skip_next_turn is False


def test_skip_turn_action_circular_rotation():
    """Test SkipTurnAction rotates to the next player correctly"""
    game = GamePlay(stage=STAGE_CHARACTER_SELECT, active=ActivePlayer1(player="player2"))
    characters_p1 = init_characters()
    characters_p2 = init_characters()

    # Player 2 has no available characters
    kill_character(characters_p2, CHARACTER_KNIGHT)
    kill_character(characters_p2, CHARACTER_ARCHER)
    characters_p2[CHARACTER_MAGE].effects = [EFFECT_SKIP_TURN]

    game.players["player1"] = Player(name="player1", characters=characters_p1)
    game.players["player2"] = Player(name="player2", characters=characters_p2)

    action = SkipTurnAction("player2", game)
    updated_game = action.run()

    # Should rotate back to player1
    assert updated_game.active.player == "player1"
    assert updated_game.stage == STAGE_CHARACTER_SELECT
