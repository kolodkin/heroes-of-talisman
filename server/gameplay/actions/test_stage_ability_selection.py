"""
Tests for Ability Selection Stage Actions.

These tests verify ability selection behavior including highlighting
selected abilities and confirming selections to transition to:
- ability_opponent_selection (for effects requiring target selection, e.g., FREEZE)
- opponent_selection (for effects applied to battle opponent, e.g., BATTLE_HOWL, BOUNCING_ARROW)
"""

import pytest

from .stage_ability_selection import AbilityPressAction, AbilitySelectAction
from ..models import (
    GameException,
    ReportedException,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    CHARACTER_SELECT,
    KNIGHT,
    ARCHER,
    MAGE,
    REROLL_DICE,
)
from ..abilities import BATTLE_HOWL, BOUNCING_ARROW, FREEZE
from ..effects import RerollDiceEffect
from ..gameplay import (
    GamePlay,
    Player,
    ActivePlayer2,
    init_characters,
)


def test_ability_press_action_valid():
    """Test pressing an ability highlights it in stage_meta"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)
    updated_game = action.run(ability=BATTLE_HOWL)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == BATTLE_HOWL
    assert updated_game.stage == ABILITY_SELECTION  # Still in ability selection


def test_ability_press_action_not_active_player():
    """Test pressing ability when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = AbilityPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(ability=BATTLE_HOWL)


def test_ability_press_action_wrong_stage():
    """Test pressing ability in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(ability=BATTLE_HOWL)


def test_ability_press_action_invalid_ability():
    """Test pressing ability not available for character raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)

    # Knight should have BATTLE_HOWL, not FREEZE (which is for mage)
    with pytest.raises(ReportedException, match="not available for this character"):
        action.run(ability=FREEZE)


def test_ability_press_action_archer():
    """Test pressing archer's ability (BOUNCING_ARROW) works correctly"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)
    updated_game = action.run(ability=BOUNCING_ARROW)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == BOUNCING_ARROW


def test_ability_press_action_mage():
    """Test pressing mage's ability (FREEZE) works correctly"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=MAGE),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)
    updated_game = action.run(ability=FREEZE)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == FREEZE


def test_ability_select_action_valid():
    """Test confirming ability selection transitions to opponent_selection (for battle opponent effects)"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=BATTLE_HOWL)

    # BATTLE_HOWL applies to battle opponent, so skip ability_opponent_selection
    assert updated_game.stage == OPPONENT_SELECTION
    assert updated_game.ability is not None
    assert updated_game.ability.name == BATTLE_HOWL
    assert updated_game.stage_meta is None


def test_ability_select_action_not_active_player():
    """Test confirming ability selection when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = AbilitySelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(ability=BATTLE_HOWL)


def test_ability_select_action_wrong_stage():
    """Test confirming ability selection in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(ability=BATTLE_HOWL)


def test_ability_select_action_invalid_ability():
    """Test confirming ability not available for character raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)

    # Knight should have BATTLE_HOWL, not BOUNCING_ARROW (which is for archer)
    with pytest.raises(ReportedException, match="not available for this character"):
        action.run(ability=BOUNCING_ARROW)


def test_ability_select_action_archer():
    """Test confirming archer's ability selection skips to opponent_selection"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=BOUNCING_ARROW)

    # BOUNCING_ARROW applies to self, so skip ability_opponent_selection
    assert updated_game.stage == OPPONENT_SELECTION
    assert updated_game.ability is not None
    assert updated_game.ability.name == BOUNCING_ARROW
    assert updated_game.stage_meta is None


def test_ability_select_action_archer_applies_reroll_effect():
    """Test confirming BOUNCING_ARROW applies RerollDiceEffect to active player's character"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    # Verify archer has no effects before
    assert len(game.players["player1"].characters[ARCHER].effects) == 0

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=BOUNCING_ARROW)

    # Verify RerollDiceEffect was applied to the active player's archer
    archer = updated_game.players["player1"].characters[ARCHER]
    assert len(archer.effects) == 1
    assert isinstance(archer.effects[0], RerollDiceEffect)
    assert archer.effects[0].name == REROLL_DICE
    # Verify the effect is available in effect totals
    assert archer.effect.reroll_dice_available is True


def test_ability_select_action_mage():
    """Test confirming mage's ability selection transitions to ability_opponent_selection"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=MAGE),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=FREEZE)

    # FREEZE requires opponent selection (SkipTurnEffect), so go to ability_opponent_selection
    assert updated_game.stage == ABILITY_OPPONENT_SELECTION
    assert updated_game.ability is not None
    assert updated_game.ability.name == FREEZE
    assert updated_game.stage_meta is None
