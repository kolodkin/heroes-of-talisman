"""
Tests for Ability Item Selection Stage Actions.

These tests verify that:
- AbilityItemPressAction highlights a selected item card in stage_meta
- AbilityItemSelectAction removes the selected item and transitions to opponent_selection
- Error cases (wrong stage, wrong player, no item selected, etc.) are handled correctly
"""

import pytest

from .stage_ability_item_selection import AbilityItemPressAction, AbilityItemSelectAction
from ..common import GameException, ReportedException, CHARACTER_KNIGHT, CHARACTER_MAGE
from ..abilities import ABILITY_DRAGON_BREATH
from ..cards import CARD_METAL_ARMOR, CARD_SACRED_SWORD
from ..gameplay import (
    STAGE_ABILITY_ITEM_SELECTION,
    STAGE_OPPONENT_SELECTION,
    GamePlay,
    Player,
    ActivePlayer2,
    Opponent2,
    AbilityItemMeta,
    init_characters,
)


# ──────────────────────────────────────────────
# AbilityItemPressAction tests
# ──────────────────────────────────────────────

def test_ability_item_press_highlights_selected_item():
    """Pressing an item card sets stage_meta.selected_item to that card name."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR, CARD_SACRED_SWORD]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(target_player="player2", target_character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemPressAction("player1", game)
    updated_game = action.run(item=CARD_METAL_ARMOR)

    assert updated_game.stage == STAGE_ABILITY_ITEM_SELECTION
    assert updated_game.stage_meta.selected_item == CARD_METAL_ARMOR


def test_ability_item_press_changes_selection():
    """Pressing a different item card changes stage_meta.selected_item."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR, CARD_SACRED_SWORD]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(target_player="player2", target_character=CHARACTER_KNIGHT, selected_item=CARD_METAL_ARMOR),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemPressAction("player1", game)
    updated_game = action.run(item=CARD_SACRED_SWORD)

    assert updated_game.stage_meta.selected_item == CARD_SACRED_SWORD


def test_ability_item_press_not_active_player():
    """Non-active player cannot press an item."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(target_player="player2", target_character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(item=CARD_METAL_ARMOR)


def test_ability_item_press_wrong_stage():
    """Pressing an item in the wrong stage raises GameException."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(target_player="player2", target_character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(item=CARD_METAL_ARMOR)


def test_ability_item_press_invalid_item():
    """Pressing an item not in target's active_cards raises ReportedException."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(target_player="player2", target_character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemPressAction("player1", game)

    with pytest.raises(ReportedException, match="not in target's active cards"):
        action.run(item=CARD_SACRED_SWORD)


# ──────────────────────────────────────────────
# AbilityItemSelectAction tests
# ──────────────────────────────────────────────

def test_ability_item_select_removes_selected_item():
    """Selecting an item removes it from the target's active_cards."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR, CARD_SACRED_SWORD]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(
            target_player="player2",
            target_character=CHARACTER_KNIGHT,
            selected_item=CARD_METAL_ARMOR,
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemSelectAction("player1", game)
    updated_game = action.run()

    target_knight = updated_game.players["player2"].characters[CHARACTER_KNIGHT]
    assert CARD_METAL_ARMOR not in target_knight.active_cards
    assert CARD_SACRED_SWORD in target_knight.active_cards
    assert len(target_knight.active_cards) == 1


def test_ability_item_select_transitions_to_opponent_selection():
    """After item selection, stage transitions to opponent_selection."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(
            target_player="player2",
            target_character=CHARACTER_KNIGHT,
            selected_item=CARD_METAL_ARMOR,
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemSelectAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage == STAGE_OPPONENT_SELECTION
    assert updated_game.stage_meta is None


def test_ability_item_select_not_active_player():
    """Non-active player cannot confirm item selection."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(
            target_player="player2",
            target_character=CHARACTER_KNIGHT,
            selected_item=CARD_METAL_ARMOR,
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_ability_item_select_no_item_selected():
    """Confirming without selecting an item raises ReportedException."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_ABILITY_ITEM_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(target_player="player2", target_character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemSelectAction("player1", game)

    with pytest.raises(ReportedException, match="No item selected"):
        action.run()


def test_ability_item_select_wrong_stage():
    """Confirming in wrong stage raises GameException."""
    characters1 = init_characters(level=2)
    characters2 = init_characters()
    characters2[CHARACTER_KNIGHT].active_cards = [CARD_METAL_ARMOR]

    game = GamePlay(
        stage=STAGE_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        ability=ABILITY_DRAGON_BREATH,
        ability_opponent=Opponent2(player="player2", character=CHARACTER_KNIGHT),
        stage_meta=AbilityItemMeta(
            target_player="player2",
            target_character=CHARACTER_KNIGHT,
            selected_item=CARD_METAL_ARMOR,
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    action = AbilityItemSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


# ──────────────────────────────────────────────
# Dragon Breath routing to ability_item_selection
# ──────────────────────────────────────────────

def test_dragon_breath_routes_to_item_selection_when_target_has_items():
    """Dragon Breath routes to ability_item_selection when the target has active cards."""
    from .stage_ability_opponent_selection import AbilityOpponentSelectAction
    from ..gameplay import STAGE_ABILITY_OPPONENT_SELECTION

    characters1 = init_characters(level=2)
    characters2 = init_characters()
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
    assert isinstance(updated_game.stage_meta, AbilityItemMeta)
    assert updated_game.stage_meta.target_player == "player2"
    assert updated_game.stage_meta.target_character == CHARACTER_KNIGHT
    assert updated_game.stage_meta.selected_item is None


def test_dragon_breath_routes_to_opponent_selection_when_target_has_no_items():
    """Dragon Breath routes directly to opponent_selection when target has no active cards."""
    from .stage_ability_opponent_selection import AbilityOpponentSelectAction
    from ..gameplay import STAGE_ABILITY_OPPONENT_SELECTION

    characters1 = init_characters(level=2)
    characters2 = init_characters()
    # No active_cards for target

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

    assert updated_game.stage == STAGE_OPPONENT_SELECTION
