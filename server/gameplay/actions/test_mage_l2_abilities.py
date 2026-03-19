"""
Tests for Mage Level 2 abilities: Storm and Dragon Breath.

Storm (סופה): Causes the battle opponent to lose 2 attack bonuses (-2 to opponent's attacks).
Dragon Breath (נשימת דרקון): Removes one active card from a selected opponent.
"""

import pytest

from .stage_ability_selection import AbilitySelectAction
from .stage_ability_opponent_selection import AbilityOpponentSelectAction
from .stage_opponent_selection import OpponentSelectAction
from ..common import CHARACTER_KNIGHT, CHARACTER_MAGE, CHARACTER_ARCHER
from ..abilities import ABILITY_STORM, ABILITY_DRAGON_BREATH, ABILITY_FREEZE
from ..cards import CARD_METAL_ARMOR, CARD_SACRED_SWORD
from ..gameplay import (
    STAGE_ABILITY_SELECTION,
    STAGE_ABILITY_OPPONENT_SELECTION,
    STAGE_OPPONENT_SELECTION,
    STAGE_BATTLE_DICE_ROLL,
    GamePlay,
    Player,
    ActivePlayer2,
    Opponent2,
    init_characters,
)


# ──────────────────────────────────────────────
# Storm (APPLY_TO_BATTLE_OPPONENT) tests
# ──────────────────────────────────────────────

def test_storm_routes_to_opponent_selection():
    """Storm has APPLY_TO_BATTLE_OPPONENT so no separate target selection is needed."""
    characters = init_characters(level=2)
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters(level=2)),
        },
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_STORM)

    assert updated_game.stage == STAGE_OPPONENT_SELECTION
    assert updated_game.ability == ABILITY_STORM


def test_storm_applies_attack_neg_bonus_to_battle_opponent():
    """Storm applies -2 attack_neg_bonus to the battle opponent when they are selected."""
    characters1 = init_characters(level=2)
    characters2 = init_characters(level=2)
    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_STORM,
        stage_meta=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_BATTLE_DICE_ROLL

    opponent_character = updated_game.players["player2"].characters[CHARACTER_KNIGHT]
    # Storm is stored as ability name in effects
    assert ABILITY_STORM in opponent_character.effects
    # The effect total should reflect -2 attack_neg_bonus
    assert opponent_character.effect.attack_neg_bonus == -2


def test_storm_does_not_affect_mage_own_attack():
    """Storm should not apply any effects to the mage's own character."""
    characters1 = init_characters(level=2)
    characters2 = init_characters(level=2)
    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_STORM,
        stage_meta=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = OpponentSelectAction("player1", game)
    updated_game = action.run()

    mage = updated_game.players["player1"].characters[CHARACTER_MAGE]
    assert mage.effect.attack_neg_bonus == 0


def test_storm_reduces_opponent_battle_score():
    """Storm's -2 attack_neg_bonus is reflected in the opponent's effect total."""
    characters = init_characters(level=2)
    knight = characters[CHARACTER_KNIGHT]
    knight.effects = [ABILITY_STORM]

    assert knight.effect.attack_neg_bonus == -2


# ──────────────────────────────────────────────
# Dragon Breath (APPLY_TO_SELECTED_OPPONENT) tests
# ──────────────────────────────────────────────

def test_dragon_breath_routes_to_ability_opponent_selection():
    """Dragon Breath has APPLY_TO_SELECTED_OPPONENT so it requires target selection."""
    characters = init_characters(level=2)
    game = GamePlay(
        stage=STAGE_ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters(level=2)),
        },
    )

    action = AbilitySelectAction("player1", game)
    updated_game = action.run(ability=ABILITY_DRAGON_BREATH)

    assert updated_game.stage == STAGE_ABILITY_OPPONENT_SELECTION
    assert updated_game.ability == ABILITY_DRAGON_BREATH


def test_dragon_breath_routes_to_ability_item_selection_when_target_has_items():
    """Dragon Breath routes to ability_item_selection when target has active cards to choose from."""
    from ..gameplay import STAGE_ABILITY_ITEM_SELECTION, AbilityItemMeta

    characters1 = init_characters(level=2)
    characters2 = init_characters(level=2)
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR, CARD_SACRED_SWORD]

    game = GamePlay(
        stage=STAGE_ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        stage_meta=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityOpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_ABILITY_ITEM_SELECTION
    assert isinstance(updated_game.stage_meta, AbilityItemMeta)
    assert updated_game.stage_meta.target_player == "player2"
    assert updated_game.stage_meta.target_character == CHARACTER_KNIGHT
    # Items are preserved until the player selects which one to remove
    target_knight = updated_game.players["player2"].characters[CHARACTER_KNIGHT]
    assert len(target_knight.active_cards) == 2


def test_dragon_breath_no_crash_when_target_has_no_items():
    """Dragon Breath goes directly to opponent_selection when target has no active cards."""
    characters1 = init_characters(level=2)
    characters2 = init_characters(level=2)
    # Target has no active cards

    game = GamePlay(
        stage=STAGE_ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        stage_meta=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityOpponentSelectAction("player1", game)
    updated_game = action.run()

    target_knight = updated_game.players["player2"].characters[CHARACTER_KNIGHT]
    assert len(target_knight.active_cards) == 0
    assert updated_game.stage == STAGE_OPPONENT_SELECTION


def test_dragon_breath_ability_opponent_is_set_when_routing_to_item_selection():
    """ability_opponent is stored when Dragon Breath routes to ability_item_selection."""
    from ..gameplay import STAGE_ABILITY_ITEM_SELECTION

    characters1 = init_characters(level=2)
    characters2 = init_characters(level=2)
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        stage_meta=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityOpponentSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_ABILITY_ITEM_SELECTION
    assert updated_game.ability_opponent is not None
    assert updated_game.ability_opponent.player == "player2"
    assert updated_game.ability_opponent.character == CHARACTER_KNIGHT


# ──────────────────────────────────────────────
# Mage L2 character has correct abilities
# ──────────────────────────────────────────────

def test_mage_l2_has_three_abilities():
    """Level 2 mage has freeze (L1), storm, and dragon_breath."""
    characters = init_characters(level=2)
    mage = characters[CHARACTER_MAGE]

    ability_names = [a.name for a in mage.abilities]
    assert ABILITY_FREEZE in ability_names
    assert ABILITY_STORM in ability_names
    assert ABILITY_DRAGON_BREATH in ability_names
    assert len(mage.abilities) == 3
