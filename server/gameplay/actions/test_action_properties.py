"""
Tests for Action base class properties.

These tests verify that action properties work correctly across different game states.
"""

import pytest

from .action import Action
from ..common import GameException, KNIGHT, MAGE, ARCHER
from ..gameplay import (
    BATTLE_DICE_ROLL,
    CHARACTER_SELECT,
    GamePlay,
    Player,
    ActivePlayer1,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent2,
    Opponent3,
    Opponent4,
    BattleResult,
    init_characters,
    KNIGHT_L1_DEFAULT_HEALTH,
    KNIGHT_L1_DICE,
    KNIGHT_L1_ATTACK,
    MAGE_L1_DEFAULT_HEALTH,
    MAGE_L1_DICE,
    MAGE_L1_ATTACK,
    ARCHER_L1_DEFAULT_HEALTH,
    ARCHER_L1_DICE,
    ARCHER_L1_ATTACK,
)


class ConcreteAction(Action):
    """Concrete implementation of Action for testing"""

    @property
    def action_stages(self):
        return None  # No stage validation for testing

    def _run(self):
        return self.game


# ============================================================================
# active_character Property Tests
# ============================================================================


def test_active_character_with_active_player2():
    """Test active_character property with ActivePlayer2"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.active_character

    assert character.health == KNIGHT_L1_DEFAULT_HEALTH
    assert character.dice == KNIGHT_L1_DICE
    assert character.attack == KNIGHT_L1_ATTACK


def test_active_character_with_active_player3():
    """Test active_character property with ActivePlayer3"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=MAGE, dice_roll=[6]),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.active_character

    assert character.health == MAGE_L1_DEFAULT_HEALTH
    assert character.dice == MAGE_L1_DICE
    assert character.attack == MAGE_L1_ATTACK


def test_active_character_with_active_player4():
    """Test active_character property with ActivePlayer4"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer4(player="player1", character=ARCHER, dice_roll=[3], result=BattleResult(winner=True, score=3)),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.active_character

    assert character.health == ARCHER_L1_DEFAULT_HEALTH
    assert character.dice == ARCHER_L1_DICE
    assert character.attack == ARCHER_L1_ATTACK


def test_active_character_with_active_player1_fails():
    """Test active_character property fails with ActivePlayer1 (no character selected)"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    with pytest.raises(GameException, match="Active player not set or has no character selected"):
        _ = action.active_character


def test_active_character_with_no_active_fails():
    """Test active_character property fails when no active player"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=None,
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    with pytest.raises(GameException, match="Active player not set or has no character selected"):
        _ = action.active_character


# ============================================================================
# opponent_character Property Tests
# ============================================================================


def test_opponent_character_with_opponent2():
    """Test opponent_character property with Opponent2"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.opponent_character

    assert character.health == MAGE_L1_DEFAULT_HEALTH
    assert character.dice == MAGE_L1_DICE
    assert character.attack == MAGE_L1_ATTACK


def test_opponent_character_with_opponent3():
    """Test opponent_character property with Opponent3"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent3(player="player2", character=ARCHER, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.opponent_character

    assert character.health == ARCHER_L1_DEFAULT_HEALTH
    assert character.dice == ARCHER_L1_DICE
    assert character.attack == ARCHER_L1_ATTACK


def test_opponent_character_with_opponent4():
    """Test opponent_character property with Opponent4"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer4(player="player1", character=KNIGHT, dice_roll=[6], result=BattleResult(winner=True, score=7)),
        opponent=Opponent4(player="player2", character=MAGE, dice_roll=[1], result=BattleResult(winner=False, score=1)),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.opponent_character

    assert character.health == MAGE_L1_DEFAULT_HEALTH
    assert character.dice == MAGE_L1_DICE
    assert character.attack == MAGE_L1_ATTACK


def test_opponent_character_with_no_opponent_fails():
    """Test opponent_character property fails when no opponent"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=None,
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    with pytest.raises(GameException, match="Opponent not set or has no character selected"):
        _ = action.opponent_character


# ============================================================================
# player Property Tests
# ============================================================================


def test_player_property():
    """Test player property returns correct player"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    player = action.player

    assert player.name == "player1"
    assert KNIGHT in player.characters
    assert player.characters[KNIGHT].health == KNIGHT_L1_DEFAULT_HEALTH
    assert player.characters[KNIGHT].attack == KNIGHT_L1_ATTACK


def test_player_property_player_not_in_game_fails():
    """Test player property fails when player not in game"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player2", game)  # player2 not in game
    with pytest.raises(GameException, match="Player not in game"):
        _ = action.player


# ============================================================================
# stage Property Tests
# ============================================================================


def test_stage_property_get():
    """Test stage property getter"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    assert action.stage == BATTLE_DICE_ROLL


def test_stage_property_set():
    """Test stage property setter"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    action.stage = BATTLE_DICE_ROLL
    assert action.stage == BATTLE_DICE_ROLL
    assert game.stage == BATTLE_DICE_ROLL


# ============================================================================
# active and opponent Property Tests
# ============================================================================


def test_active_property_get():
    """Test active property getter"""
    characters = init_characters()
    active_player = ActivePlayer2(player="player1", character=KNIGHT)
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=active_player,
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    assert action.active == active_player
    assert action.active.player == "player1"
    assert action.active.character == KNIGHT


def test_active_property_set():
    """Test active property setter"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    new_active = ActivePlayer2(player="player1", character=MAGE)
    action.active = new_active

    assert action.active == new_active
    assert game.active == new_active


def test_opponent_property_get():
    """Test opponent property getter"""
    characters = init_characters()
    opponent = Opponent2(player="player2", character=ARCHER)
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=opponent,
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    assert action.opponent == opponent
    assert action.opponent.player == "player2"
    assert action.opponent.character == ARCHER


def test_opponent_property_set():
    """Test opponent property setter"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=None,
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    new_opponent = Opponent2(player="player2", character=MAGE)
    action.opponent = new_opponent

    assert action.opponent == new_opponent
    assert game.opponent == new_opponent
