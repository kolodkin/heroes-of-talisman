"""
Tests for Card Draw Stage Actions.

These tests verify card draw behavior including drawing a random card
and applying card effects to the character.
"""

import pytest

from .stage_card_draw import CardDrawAction, CardSelectAction
from .battle_end import BattleEndAction
from ..common import GameException, ReportedException, CHARACTER_KNIGHT, CHARACTER_MAGE, CHARACTER_ARCHER
from ..cards import CARD_METAL_ARMOR, CARD_SACRED_SWORD, CARD_GOLDEN_APPLE, CARD_TALISMAN, CARDS_MAP
from ..effects import DefenseBonusEffect, AttackBonusEffect, TalismanEffect
from ..gameplay import (
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    STAGE_CHARACTER_SELECT,
    GamePlay,
    Player,
    ActivePlayer2,
    CardDrawMeta,
    init_characters,
)
from ..gameplay import MAX_LEVEL
from ..presets import (
    get_debug_preset,
    PRESET_BATTLE_METAL_ARMOR,
    PRESET_CARD_DRAW_ARCHER_SACRED_SWORD,
    PRESET_CARD_DRAW_KNIGHT_GOLDEN_APPLE,
    PRESET_CARD_DRAW_GOLDEN_APPLE_MAX_HEALTH,
    PRESET_CARD_DRAW_KNIGHT_MAGIC_BALL_MAX_LEVEL,
    PRESET_CARD_DRAW_KNIGHT_TALISMAN,
)


def test_card_draw_action_valid():
    """Test drawing a card stores it in stage_meta"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardDrawAction("player1", game)
    updated_game = action.run()

    assert updated_game.stage_meta is not None
    assert isinstance(updated_game.stage_meta, CardDrawMeta)
    assert updated_game.stage_meta.drawn_card in CARDS_MAP
    assert updated_game.stage == STAGE_CARD_DRAW  # Still in card draw stage


def test_card_draw_action_not_active_player():
    """Test drawing card when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = CardDrawAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_card_draw_action_wrong_stage():
    """Test drawing card in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardDrawAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_card_select_action_applies_effects():
    """Test selecting a card applies its effects to the character"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_METAL_ARMOR
    assert updated_game.stage_meta is not None  # Auto-selected ability

    # Check character has defense effect
    player = updated_game.players["player1"]
    knight = player.characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], DefenseBonusEffect)
    assert knight.effects[0].defense_bonus == 2
    assert knight.effects[0].source == CARD_METAL_ARMOR
    assert knight.effects[0].dispose_actions == []  # Persistent effect

    # Check card added to character's card list
    assert CARD_METAL_ARMOR in knight.cards


def test_card_select_action_not_active_player():
    """Test selecting card when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = CardSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_card_select_action_no_card_drawn():
    """Test selecting card when no card was drawn raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)

    with pytest.raises(GameException, match="No card was drawn"):
        action.run()


def test_card_select_action_wrong_stage():
    """Test selecting card in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_metal_armor_defense_reduces_opponent_score():
    """Test metal_armor defense reduces opponent's battle score, loser still takes 1 damage"""
    # Get preset with knight having metal_armor and losing battle
    game = get_debug_preset(PRESET_BATTLE_METAL_ARMOR, player1_name="player1", player2_name="player2")

    # Knight should have defense effect before battle ends
    player1 = game.players["player1"]
    knight = player1.characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], DefenseBonusEffect)
    assert knight.effects[0].defense_bonus == 2

    # Knight's initial health
    knight_health_before = knight.health

    # End battle (knight loses, defense reduces opponent score but knight still loses)
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Knight takes 1 damage (defense affects score, not damage)
    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_after.health == knight_health_before - 1

    # Defense effect should still be present (persistent, not disposed)
    assert len(knight_after.effects) == 1
    assert isinstance(knight_after.effects[0], DefenseBonusEffect)
    assert knight_after.effects[0].defense_bonus == 2


def test_sacred_sword_applies_attack_bonus():
    """Test sacred_sword applies +3 attack bonus to knight"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_SACRED_SWORD

    # Check character has attack bonus effect
    player = updated_game.players["player1"]
    knight = player.characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], AttackBonusEffect)
    assert knight.effects[0].attack_bonus == 3
    assert knight.effects[0].source == CARD_SACRED_SWORD
    assert knight.effects[0].dispose_actions == []

    # Check card added to character's card list
    assert CARD_SACRED_SWORD in knight.cards


def test_sacred_sword_rejected_by_archer():
    """Test sacred_sword is not added when archer tries to use it"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_ARCHER),
        stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state transitions correctly
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_SACRED_SWORD

    # Verify archer doesn't have the effect (restricted character)
    player = updated_game.players["player1"]
    archer = player.characters[CHARACTER_ARCHER]
    assert len(archer.effects) == 0

    # Card should NOT be added to character's card list (restricted character)
    assert CARD_SACRED_SWORD not in archer.cards


def test_sacred_sword_works_for_mage():
    """Test sacred_sword works fine for mage"""
    characters = init_characters()
    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_MAGE),
        stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_SACRED_SWORD

    # Check mage has attack bonus effect
    player = updated_game.players["player1"]
    mage = player.characters[CHARACTER_MAGE]
    assert len(mage.effects) == 1
    assert isinstance(mage.effects[0], AttackBonusEffect)
    assert mage.effects[0].attack_bonus == 3


def test_sacred_sword_archer_restriction_from_preset():
    """Test archer sacred_sword restriction using the preset"""
    game = get_debug_preset(PRESET_CARD_DRAW_ARCHER_SACRED_SWORD)

    # Verify preset is set up correctly
    assert game.stage == STAGE_CARD_DRAW
    assert game.active.character == CHARACTER_ARCHER
    assert game.stage_meta.drawn_card == CARD_SACRED_SWORD

    # Execute card selection
    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Verify restriction behavior
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    player = updated_game.players["player1"]
    archer = player.characters[CHARACTER_ARCHER]

    # Archer should not have the effect
    assert len(archer.effects) == 0

    # Card should not be added to archer's card list
    assert CARD_SACRED_SWORD not in archer.cards


def test_golden_apple_heals_damaged_knight():
    """Test golden_apple heals knight from 1 to 2 health using preset"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_GOLDEN_APPLE)

    # Verify preset: knight at 1 health
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.health == 1

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check knight healed to 2
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.health == 2
    assert CARD_GOLDEN_APPLE in knight.cards


def test_golden_apple_does_not_exceed_max_health():
    """Test golden_apple healing is capped at max_health using preset"""
    game = get_debug_preset(PRESET_CARD_DRAW_GOLDEN_APPLE_MAX_HEALTH)

    # Verify preset: knight at max health (2/2)
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.health == knight_before.max_health

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check character health doesn't exceed max
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.health == 2  # Still at max, not 3
    assert knight.health <= knight.max_health
    assert CARD_GOLDEN_APPLE in knight.cards


def test_magic_ball_no_effect_at_max_level():
    """Test magic_ball has no effect when knight is already at MAX_LEVEL"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_MAGIC_BALL_MAX_LEVEL)

    # Verify preset: knight at max level with damaged health
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.level == MAX_LEVEL
    assert knight_before.health == 4  # Damaged (max is 5)
    assert knight_before.max_health == 5
    assert knight_before.dice == 2
    assert knight_before.attack == 3

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Verify no stats changed
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.level == MAX_LEVEL  # Still at max level
    assert knight.health == 4  # Health NOT restored (no level up occurred)
    assert knight.max_health == 5
    assert knight.dice == 2
    assert knight.attack == 3


def test_talisman_card_applies_effect():
    """Test talisman card applies TalismanEffect as persistent effect"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_TALISMAN)

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_TALISMAN

    # Check character has talisman effect
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert len(knight.effects) == 1
    assert isinstance(knight.effects[0], TalismanEffect)
    assert knight.effects[0].source == CARD_TALISMAN
    assert knight.effects[0].dispose_actions == []  # Persistent effect

    # Check card added to character's card list
    assert CARD_TALISMAN in knight.cards

    # Check effect aggregation
    assert knight.effect.has_talisman is True
