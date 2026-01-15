"""
Tests for Opponent Selection Stage Actions.

These tests verify opponent selection behavior including highlighting
selected opponents and confirming selections to transition to battle.
"""

import pytest

from .stage_opponent_selection import (
    OpponentPressAction,
    OpponentSelectAction,
)
from ..models import (
    GamePlay,
    Player,
    Ability,
    CharacterCard,
    ActivePlayer2,
    GameException,
    ReportedException,
    Opponent2,
    AttackNegBonusEffect,
    CHARACTER_DEFAULT_STATS,
    OPPONENT_SELECTION,
    BATTLE_DICE_ROLL,
    KNIGHT,
    ARCHER,
    MAGE,
    BATTLE_HOWL,
    ATTACK_NEG_BONUS,
    ABILITIES_MAP,
    init_characters,
)


def test_opponent_press_action_valid():
    """Test pressing opponent's character highlights it in stage_meta"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentPressAction("player1", game)
    updated_game = action.run(opponent="player2", character=KNIGHT)

    assert updated_game.stage_meta is not None
    assert isinstance(updated_game.stage_meta, Opponent2)
    assert updated_game.stage_meta.player == "player2"
    assert updated_game.stage_meta.character == KNIGHT
    assert (
        updated_game.stage == OPPONENT_SELECTION
    )  # Still in opponent selection


def test_opponent_press_action_not_active_player():
    """Test pressing opponent when not active player raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(opponent="player1", character=KNIGHT)


def test_opponent_press_action_wrong_stage():
    """Test pressing opponent in wrong stage raises error"""
    game = GamePlay(stage=BATTLE_DICE_ROLL, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(opponent="player2", character=KNIGHT)


def test_opponent_press_action_invalid_opponent():
    """Test pressing non-existent opponent raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = OpponentPressAction("player1", game)

    with pytest.raises(ReportedException, match="not in game"):
        action.run(opponent="player2", character=KNIGHT)


def test_opponent_press_action_self_as_opponent():
    """Test pressing self as opponent raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = OpponentPressAction("player1", game)

    with pytest.raises(
        ReportedException, match="Cannot select yourself as opponent"
    ):
        action.run(opponent="player1", character=KNIGHT)


def test_opponent_press_action_invalid_character():
    """Test pressing non-existent character for opponent raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    player1_characters = {
        KNIGHT: CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[KNIGHT])
    }
    player2_characters = {}  # No characters
    game.players["player1"] = Player(
        name="player1", characters=player1_characters
    )
    game.players["player2"] = Player(
        name="player2", characters=player2_characters
    )

    action = OpponentPressAction("player1", game)

    with pytest.raises(ReportedException, match="not available for opponent"):
        action.run(opponent="player2", character=KNIGHT)


def test_opponent_select_action_valid():
    """Test confirming opponent selection transitions to battle"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    # Set stage_meta with selected opponent
    game.stage_meta = Opponent2(player="player2", character=KNIGHT)

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.opponent is not None
    assert updated_game.opponent.player == "player2"
    assert updated_game.opponent.character == KNIGHT
    assert updated_game.stage == BATTLE_DICE_ROLL
    assert updated_game.stage_meta is None  # Cleared after transition


def test_opponent_select_action_not_active_player():
    """Test confirming selection when not active player raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    # Set stage_meta with selected opponent
    game.stage_meta = Opponent2(player="player2", character=KNIGHT)

    action = OpponentSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_opponent_select_action_wrong_stage():
    """Test confirming selection in wrong stage raises error"""
    game = GamePlay(stage=BATTLE_DICE_ROLL, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_opponent_select_action_no_opponent_selected():
    """Test confirming with no opponent selected raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="No opponent selected"):
        action.run()


def test_opponent_press_action_dead_character():
    """Test pressing a dead opponent character raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters_p1 = init_characters()
    characters_p2 = init_characters()
    # Kill opponent's knight
    characters_p2[KNIGHT].health = 0
    game.players["player1"] = Player(name="player1", characters=characters_p1)
    game.players["player2"] = Player(name="player2", characters=characters_p2)

    action = OpponentPressAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        action.run(opponent="player2", character=KNIGHT)


def test_opponent_select_action_dead_character():
    """Test confirming selection of a dead opponent character raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters_p1 = init_characters()
    characters_p2 = init_characters()
    # Kill opponent's knight
    characters_p2[KNIGHT].health = 0
    game.players["player1"] = Player(name="player1", characters=characters_p1)
    game.players["player2"] = Player(name="player2", characters=characters_p2)

    # Set stage_meta with dead character
    game.stage_meta = Opponent2(player="player2", character=KNIGHT)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be selected"):
        action.run()


def test_opponent_select_action_with_self_effect_ability():
    """Test confirming opponent selection when ability has self effects (already applied in AbilitySelectAction)"""
    game = GamePlay(stage=OPPONENT_SELECTION, active=ActivePlayer2(player="player1", character=KNIGHT))
    characters_p1 = init_characters()
    characters_p2 = init_characters()
    game.players["player1"] = Player(name="player1", characters=characters_p1)
    game.players["player2"] = Player(name="player2", characters=characters_p2)

    # Set ability to BATTLE_HOWL (has AttackBonusEffect with apply_to='self')
    # Note: Self effects are applied in AbilitySelectAction, not here
    game.ability = ABILITIES_MAP[BATTLE_HOWL]

    # Set stage_meta with selected opponent
    game.stage_meta = Opponent2(player="player2", character=MAGE)

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    # Verify opponent's mage has no effects (self effects don't apply to opponent)
    opponent_mage = updated_game.players["player2"].characters[MAGE]
    assert len(opponent_mage.effects) == 0

    # Verify game transitioned to battle stage
    assert updated_game.stage == BATTLE_DICE_ROLL
