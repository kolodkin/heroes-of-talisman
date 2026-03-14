"""
Tests for Card Draw Stage Actions.

These tests verify card draw behavior including drawing a random card
and applying card effects to the character.
"""

import pytest

from .stage_card_draw import CardDrawAction, CardSelectAction
from .battle_end import BattleEndAction
from ..common import GameException, ReportedException, CHARACTER_KNIGHT, CHARACTER_MAGE, CHARACTER_ARCHER
from ..cards import CARD_METAL_ARMOR, CARD_SACRED_SWORD, CARD_GOLDEN_APPLE, CARD_DEVILS_FORK, CARD_TALISMAN, CARD_FOG, CARDS_MAP
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
from ..effects import EFFECT_SKIP_TURN
from ..presets import (
    get_debug_preset,
    PRESET_BATTLE_METAL_ARMOR,
    PRESET_CARD_DRAW_ARCHER_SACRED_SWORD,
    PRESET_CARD_DRAW_KNIGHT_GOLDEN_APPLE,
    PRESET_CARD_DRAW_GOLDEN_APPLE_MAX_HEALTH,
    PRESET_CARD_DRAW_KNIGHT_DEVILS_FORK,
    PRESET_CARD_DRAW_KNIGHT_DEVILS_FORK_MIN_LEVEL,
    PRESET_CARD_DRAW_KNIGHT_MAGIC_BALL_MAX_LEVEL,
    PRESET_CARD_DRAW_KNIGHT_TALISMAN,
    PRESET_CARD_DRAW_FOG_ALL_HIGH_LEVEL,
    PRESET_CARD_DRAW_FOG_MIXED_LEVEL,
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

    # Check character has defense effect via active_cards
    player = updated_game.players["player1"]
    knight = player.characters[CHARACTER_KNIGHT]
    assert CARD_METAL_ARMOR in knight.active_cards
    assert knight.effect.defense_bonus == 2

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

    # Knight should have defense effect via active_cards before battle ends
    player1 = game.players["player1"]
    knight = player1.characters[CHARACTER_KNIGHT]
    assert CARD_METAL_ARMOR in knight.active_cards
    assert knight.effect.defense_bonus == 2

    # Knight's initial health
    knight_health_before = knight.health

    # End battle (knight loses, defense reduces opponent score but knight still loses)
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Knight takes 1 damage (defense affects score, not damage)
    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_after.health == knight_health_before - 1

    # Defense effect should still be present (persistent card, not disposed)
    assert CARD_METAL_ARMOR in knight_after.active_cards
    assert knight_after.effect.defense_bonus == 2


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

    # Check character has attack bonus via active_cards
    player = updated_game.players["player1"]
    knight = player.characters[CHARACTER_KNIGHT]
    assert CARD_SACRED_SWORD in knight.active_cards
    assert knight.effect.attack_bonus == 3

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
    assert len(archer.active_cards) == 0

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

    # Check mage has attack bonus via active_cards
    player = updated_game.players["player1"]
    mage = player.characters[CHARACTER_MAGE]
    assert CARD_SACRED_SWORD in mage.active_cards
    assert mage.effect.attack_bonus == 3


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

    # Archer should not have the card in active_cards
    assert len(archer.active_cards) == 0

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
    """Test talisman card applies TalismanEffect as persistent card"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_TALISMAN)

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check game state
    assert updated_game.stage == STAGE_ABILITY_SELECTION
    assert updated_game.card == CARD_TALISMAN

    # Check character has talisman via active_cards
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert CARD_TALISMAN in knight.active_cards

    # Check card added to character's card list
    assert CARD_TALISMAN in knight.cards

    # Check effect aggregation
    assert knight.effect.has_talisman is True


def test_devils_fork_reduces_level():
    """Test devils_fork reduces knight level from 2 to 1, health = max(current, new_max)"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_DEVILS_FORK)

    # Verify preset: knight at level 2 with 2 health (damaged)
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.level == 2
    assert knight_before.health == 2
    assert knight_before.max_health == 3
    assert knight_before.dice == 1
    assert knight_before.attack == 3

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Check knight leveled down to 1
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.level == 1
    assert knight.max_health == 2
    assert knight.dice == 1
    assert knight.attack == 1
    # Health = max(2, 2) = 2 (current health preserved)
    assert knight.health == 2
    assert CARD_DEVILS_FORK in knight.cards


def test_devils_fork_no_effect_at_min_level():
    """Test devils_fork has no effect when knight is already at level 1"""
    game = get_debug_preset(PRESET_CARD_DRAW_KNIGHT_DEVILS_FORK_MIN_LEVEL)

    # Verify preset: knight at level 1 with 1 health (damaged)
    knight_before = game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_before.level == 1
    assert knight_before.health == 1
    assert knight_before.max_health == 2
    assert knight_before.dice == 1
    assert knight_before.attack == 1

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    # Verify no stats changed
    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight.level == 1
    assert knight.health == 1  # Health NOT changed
    assert knight.max_health == 2
    assert knight.dice == 1
    assert knight.attack == 1


def test_devils_fork_health_preserved_when_above_new_max():
    """Test devils_fork preserves health when current > new level max_health"""
    # Knight L2: max_health=3, set health=3 (full)
    # After level down to L1: max_health=2, health = max(3, 2) = 3
    characters = init_characters(level=2)
    knight = characters[CHARACTER_KNIGHT]
    knight.health = 3  # Full health at L2

    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_KNIGHT),
        stage_meta=CardDrawMeta(drawn_card=CARD_DEVILS_FORK),
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_after.level == 1
    assert knight_after.max_health == 2
    # Health is max(3, 2) = 3 (current health exceeds new max, preserved)
    assert knight_after.health == 3


def test_fog_no_skip_turn_when_all_chars_high_level():
    """Test fog does NOT apply skip_turn when ALL active player's alive chars are level 3+ (they resist fog)"""
    game = get_debug_preset(PRESET_CARD_DRAW_FOG_ALL_HIGH_LEVEL)

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    p1_chars = updated_game.players["player1"].characters
    # All player1 characters at level 3 → fog does NOT apply (player resists fog)
    for char in p1_chars.values():
        assert EFFECT_SKIP_TURN not in char.effects

    p2_chars = updated_game.players["player2"].characters
    # player2 is not affected (only active player is checked)
    for char in p2_chars.values():
        assert EFFECT_SKIP_TURN not in char.effects


def test_fog_applies_skip_turn_when_mixed_levels():
    """Test fog applies skip_turn to active player's alive chars when not ALL chars are level 3+"""
    game = get_debug_preset(PRESET_CARD_DRAW_FOG_MIXED_LEVEL)

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    p1_chars = updated_game.players["player1"].characters
    # player1 has mixed levels (knight=3, others=1) → fog applies skip_turn to all alive chars
    for char in p1_chars.values():
        assert EFFECT_SKIP_TURN in char.effects

    p2_chars = updated_game.players["player2"].characters
    # player2 is not affected (only active player is checked)
    for char in p2_chars.values():
        assert EFFECT_SKIP_TURN not in char.effects


def test_fog_dead_chars_excluded_all_alive_high_level():
    """Test fog checks only alive chars: dead knight + alive archer/mage all L3+ → no skip_turn"""
    # player1: knight dead, archer L3, mage L3 → all ALIVE chars are level 3+ → fog does NOT apply
    characters_p1 = init_characters(level=3)
    characters_p1[CHARACTER_KNIGHT].health = 0
    characters_p1[CHARACTER_KNIGHT].is_alive = False

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_CARD_DRAW,
        active=ActivePlayer2(player="player1", character=CHARACTER_ARCHER),
        stage_meta=CardDrawMeta(drawn_card=CARD_FOG),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    p1_chars = updated_game.players["player1"].characters
    # All alive chars (archer, mage) are level 3+ → fog does NOT apply
    assert EFFECT_SKIP_TURN not in p1_chars[CHARACTER_ARCHER].effects
    assert EFFECT_SKIP_TURN not in p1_chars[CHARACTER_MAGE].effects
    assert EFFECT_SKIP_TURN not in p1_chars[CHARACTER_KNIGHT].effects


def test_fog_card_added_to_character_cards():
    """Test fog card is added to character's card history"""
    game = get_debug_preset(PRESET_CARD_DRAW_FOG_MIXED_LEVEL)

    action = CardSelectAction("player1", game)
    updated_game = action.run()

    knight = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert CARD_FOG in knight.cards
