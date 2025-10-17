"""
Tests for Action base class properties.

These tests verify that action properties work correctly across different game states.
"""

import pytest

from .action import Action
from ..models import (
    GamePlay,
    Player,
    ActivePlayer1,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent2,
    Opponent3,
    Opponent4,
    GameException,
    BATTLE,
    CHARACTER_SELECT,
    KNIGHT,
    MAGE,
    ARCHER,
    init_characters,
)


class ConcreteAction(Action):
    """Concrete implementation of Action for testing"""

    def run(self):
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

    assert character.health == 2  # Knight has 2 health
    assert character.dice == 1
    assert character.attack == 1


def test_active_character_with_active_player3():
    """Test active_character property with ActivePlayer3"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE,
        active=ActivePlayer3(player="player1", character=MAGE, dice_roll=[6]),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.active_character

    assert character.health == 2  # Mage has 2 health
    assert character.dice == 1
    assert character.attack is None


def test_active_character_with_active_player4():
    """Test active_character property with ActivePlayer4"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE,
        active=ActivePlayer4(player="player1", character=ARCHER, dice_roll=[3], winner=True),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.active_character

    assert character.health == 3  # Archer has 3 health
    assert character.dice == 1
    assert character.attack is None


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
        stage=BATTLE,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.opponent_character

    assert character.health == 2  # Mage has 2 health
    assert character.dice == 1
    assert character.attack is None


def test_opponent_character_with_opponent3():
    """Test opponent_character property with Opponent3"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent3(player="player2", character=ARCHER, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.opponent_character

    assert character.health == 3  # Archer has 3 health
    assert character.dice == 1
    assert character.attack is None


def test_opponent_character_with_opponent4():
    """Test opponent_character property with Opponent4"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE,
        active=ActivePlayer4(player="player1", character=KNIGHT, dice_roll=[6], winner=True),
        opponent=Opponent4(player="player2", character=MAGE, dice_roll=[1], winner=False),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    character = action.opponent_character

    assert character.health == 2
    assert character.dice == 1
    assert character.attack is None


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
    assert player.characters[KNIGHT].health == 2  # Knight has 2 health
    assert player.characters[KNIGHT].attack == 1


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
        stage=BATTLE,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ConcreteAction("player1", game)
    assert action.stage == BATTLE


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
    action.stage = BATTLE
    assert action.stage == BATTLE
    assert game.stage == BATTLE


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
        stage=BATTLE,
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
        stage=BATTLE,
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
