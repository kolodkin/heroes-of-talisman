"""
Tests for Ability Selection Stage Actions.

These tests verify ability selection behavior including highlighting
selected abilities and confirming selections to transition to:
- ability_opponent_selection (for effects requiring target selection, e.g., ABILITY_FREEZE)
- opponent_selection (for effects applied to battle opponent, e.g., ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW)
"""

import pytest

from .stage_ability_selection import AbilityPressAction, AbilitySelectAction
from ..common import (
    GameException,
    ReportedException,
    CHARACTER_KNIGHT,
    CHARACTER_ARCHER,
    CHARACTER_MAGE,
)
from ..abilities import ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE
from ..gameplay import (
    STAGE_ABILITY_SELECTION,
    STAGE_ABILITY_OPPONENT_SELECTION,
    STAGE_OPPONENT_SELECTION,
    STAGE_CHARACTER_SELECT,
)
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
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)
    updated_game = action.run(ability=ABILITY_BATTLE_HOWL)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == ABILITY_BATTLE_HOWL
    assert updated_game.stage == STAGE_ABILITY_SELECTION  # Still in ability selection


def test_ability_press_action_not_active_player():
    """Test pressing ability when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = AbilityPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(ability=ABILITY_BATTLE_HOWL)


def test_ability_press_action_wrong_stage():
    """Test pressing ability in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(ability=ABILITY_BATTLE_HOWL)


def test_ability_press_action_invalid_ability():
    """Test pressing ability not available for character raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)

    # Knight should have ABILITY_BATTLE_HOWL, not ABILITY_FREEZE (which is for mage)
    with pytest.raises(ReportedException, match="not available for this character"):
        action.run(ability=ABILITY_FREEZE)


def test_ability_press_action_archer():
    """Test pressing archer's ability (ABILITY_BOUNCING_ARROW) works correctly"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)
    updated_game = action.run(ability=ABILITY_BOUNCING_ARROW)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == ABILITY_BOUNCING_ARROW


def test_ability_press_action_mage():
    """Test pressing mage's ability (ABILITY_FREEZE) works correctly"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityPressAction("player1", game)
    updated_game = action.run(ability=ABILITY_FREEZE)

    assert updated_game.stage_meta is not None
    assert updated_game.stage_meta.selected == ABILITY_FREEZE


def test_ability_select_action_valid():
    """Test confirming ability selection transitions to opponent_selection (for battle opponent effects)"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_BATTLE_HOWL)

    # ABILITY_BATTLE_HOWL applies to battle opponent, so skip ability_opponent_selection
    assert updated_game.stage == STAGE_OPPONENT_SELECTION
    assert updated_game.ability is not None
    assert updated_game.ability.name == ABILITY_BATTLE_HOWL
    assert updated_game.stage_meta is None


def test_ability_select_action_not_active_player():
    """Test confirming ability selection when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = AbilitySelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(ability=ABILITY_BATTLE_HOWL)


def test_ability_select_action_wrong_stage():
    """Test confirming ability selection in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(ability=ABILITY_BATTLE_HOWL)


def test_ability_select_action_invalid_ability():
    """Test confirming ability not available for character raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)

    # Knight should have ABILITY_BATTLE_HOWL, not ABILITY_BOUNCING_ARROW (which is for archer)
    with pytest.raises(ReportedException, match="not available for this character"):
        action.run(ability=ABILITY_BOUNCING_ARROW)


def test_ability_select_action_archer():
    """Test confirming archer's ability selection skips to opponent_selection"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_BOUNCING_ARROW)

    # ABILITY_BOUNCING_ARROW applies to self, so skip ability_opponent_selection
    assert updated_game.stage == STAGE_OPPONENT_SELECTION
    assert updated_game.ability is not None
    assert updated_game.ability.name == ABILITY_BOUNCING_ARROW
    assert updated_game.stage_meta is None


def test_ability_select_action_archer_applies_reroll_effect():
    """Test confirming ABILITY_BOUNCING_ARROW adds bouncing_arrow to active_abilities"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    # Verify archer has no active abilities before
    assert len(game.players["player1"].characters[CHARACTER_ARCHER].active_abilities) == 0

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_BOUNCING_ARROW)

    # Verify bouncing_arrow was added to active_abilities
    archer = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert len(archer.active_abilities) == 1
    assert archer.active_abilities[0] == ABILITY_BOUNCING_ARROW
    # Verify the effect is available in effect totals
    assert archer.effect.reroll_dice_available is True


def test_ability_select_action_mage():
    """Test confirming mage's ability selection transitions to ability_opponent_selection"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_FREEZE)

    # ABILITY_FREEZE requires opponent selection (SkipTurnEffect), so go to ability_opponent_selection
    assert updated_game.stage == STAGE_ABILITY_OPPONENT_SELECTION
    assert updated_game.ability is not None
    assert updated_game.ability.name == ABILITY_FREEZE
    assert updated_game.stage_meta is None
