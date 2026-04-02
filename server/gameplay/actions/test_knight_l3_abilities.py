"""
Tests for Knight Level 3 abilities: Backhand Strike and Triple Strike.

Backhand Strike: Battle opponent gets skip_turn for next turn.
Triple Strike: Removes ALL active cards (items) from the battle opponent.
"""

from .stage_ability_selection import AbilitySelectAction
from .stage_opponent_selection import OpponentSelectAction
from ..common import CHARACTER_KNIGHT, CHARACTER_MAGE
from ..abilities import ABILITY_BACKHAND_STRIKE, ABILITY_TRIPLE_STRIKE, ABILITY_BATTLE_HOWL
from ..cards import CARD_METAL_ARMOR, CARD_SACRED_SWORD
from ..gameplay import (
    STAGE_ABILITY_SELECTION,
    STAGE_OPPONENT_SELECTION,
    STAGE_BATTLE_DICE_ROLL,
    GamePlay,
    Player,
    ActivePlayer2,
    Opponent2,
    init_characters,
)


# ──────────────────────────────────────────────
# Backhand Strike (APPLY_TO_BATTLE_OPPONENT) tests
# ──────────────────────────────────────────────

def test_backhand_strike_routes_to_opponent_selection():
    """Backhand Strike has APPLY_TO_BATTLE_OPPONENT so no separate target selection is needed."""
    characters = init_characters(level=3)
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_BACKHAND_STRIKE)

    assert updated_game.stage == STAGE_OPPONENT_SELECTION
    assert updated_game.ability == ABILITY_BACKHAND_STRIKE


def test_backhand_strike_applies_skip_turn_to_battle_opponent():
    """Backhand Strike applies skip_turn effect to the battle opponent when they are selected."""
    characters1 = init_characters(level=3)
    characters2 = init_characters()
    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        ability=ABILITY_BACKHAND_STRIKE,
        stage_meta=Opponent2(player="player2", character=CHARACTER_MAGE),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_BATTLE_DICE_ROLL

    opponent_character = updated_game.players["player2"].characters[CHARACTER_MAGE]
    # Backhand strike is stored as ability name in effects
    assert ABILITY_BACKHAND_STRIKE in opponent_character.effects
    # The effect total should reflect skip_next_turn
    assert opponent_character.effect.skip_next_turn is True


def test_backhand_strike_does_not_affect_knight_own_character():
    """Backhand Strike should not apply any effects to the knight's own character."""
    characters1 = init_characters(level=3)
    characters2 = init_characters()
    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        ability=ABILITY_BACKHAND_STRIKE,
        stage_meta=Opponent2(player="player2", character=CHARACTER_MAGE),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.effect.skip_next_turn is False


# ──────────────────────────────────────────────
# Triple Strike (NeutralizeAllItemsEffect) tests
# ──────────────────────────────────────────────

def test_triple_strike_routes_to_opponent_selection():
    """Triple Strike has APPLY_TO_BATTLE_OPPONENT so no separate target selection is needed."""
    characters = init_characters(level=3)
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_TRIPLE_STRIKE)

    assert updated_game.stage == STAGE_OPPONENT_SELECTION
    assert updated_game.ability == ABILITY_TRIPLE_STRIKE


def test_triple_strike_removes_all_items_from_battle_opponent():
    """Triple Strike removes ALL active cards from the battle opponent."""
    characters1 = init_characters(level=3)
    characters2 = init_characters()
    characters2[CHARACTER_MAGE].active_cards = [CARD_METAL_ARMOR, CARD_SACRED_SWORD]

    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        ability=ABILITY_TRIPLE_STRIKE,
        stage_meta=Opponent2(player="player2", character=CHARACTER_MAGE),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_BATTLE_DICE_ROLL

    opponent_character = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert opponent_character.active_cards == []


def test_triple_strike_no_items_is_noop():
    """Triple Strike with no items on opponent is a no-op (no crash)."""
    characters1 = init_characters(level=3)
    characters2 = init_characters()

    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        ability=ABILITY_TRIPLE_STRIKE,
        stage_meta=Opponent2(player="player2", character=CHARACTER_MAGE),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_BATTLE_DICE_ROLL
    opponent_character = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert opponent_character.active_cards == []


# ──────────────────────────────────────────────
# Knight L3 character has correct abilities
# ──────────────────────────────────────────────

def test_knight_l3_has_two_abilities():
    """Level 3 knight has backhand_strike and triple_strike (not battle_howl)."""
    characters = init_characters(level=3)
    knight = characters[CHARACTER_KNIGHT]

    ability_names = [a.name for a in knight.abilities]
    assert ABILITY_BACKHAND_STRIKE in ability_names
    assert ABILITY_TRIPLE_STRIKE in ability_names
    assert ABILITY_BATTLE_HOWL not in ability_names
    assert len(knight.abilities) == 2
