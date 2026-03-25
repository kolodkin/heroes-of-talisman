"""
Tests for Archer Level 3 skills:
  1. bouncing_arrow_l2 (חץ קופץ) — same behavior as Archer L2
  2. burning_arrow (חץ בוער) — no damage this turn, 2 damage to target on archer's next turn

Burning Arrow flow:
  1. Archer L3 selects burning_arrow ability
  2. Archer wins battle → burning_arrow:player2:mage stored on archer's effects (no damage this turn)
  3. Archer loses battle → normal loss damage to archer, no burning effect stored
  4. Archer's next turn (CharacterSelectAction) → 2 damage applied to mage, effect cleared
  5. Archer's next turn (SkipTurnAction) → 2 damage applied to mage, effect cleared
"""

import pytest

from .battle_end import BattleEndAction
from .stage_character_select import CharacterSelectAction, SkipTurnAction
from ..common import CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE
from ..abilities import ABILITY_BOUNCING_ARROW_L2, ABILITY_BURNING_ARROW
from ..effects import EFFECT_BURNING_ARROW, EFFECT_SKIP_TURN
from ..gameplay import (
    STAGE_BATTLE_END,
    STAGE_CHARACTER_SELECT,
    STAGE_BATTLE_DICE_ROLL,
    GamePlay,
    Player,
    ActivePlayer1,
    ActivePlayer4,
    Opponent4,
    BattleResult,
    init_characters,
)
from ..presets import (
    get_debug_preset,
    PRESET_ABILITY_SELECTION_ARCHER_L3,
    PRESET_BURNING_ARROW_WIN,
    PRESET_BURNING_ARROW_NEXT_TURN,
)


def test_archer_l3_has_bouncing_arrow_l2_and_burning_arrow():
    """Archer L3 should have both bouncing_arrow_l2 and burning_arrow abilities."""
    characters = init_characters(level=3)
    archer = characters[CHARACTER_ARCHER]
    ability_names = [a.name for a in archer.abilities]
    assert ABILITY_BOUNCING_ARROW_L2 in ability_names
    assert ABILITY_BURNING_ARROW in ability_names


def test_archer_l3_ability_selection_preset():
    """Archer L3 ability selection preset has correct setup with two abilities."""
    game = get_debug_preset(PRESET_ABILITY_SELECTION_ARCHER_L3)
    archer = game.players["player1"].characters[CHARACTER_ARCHER]
    ability_names = [a.name for a in archer.abilities]
    assert ABILITY_BOUNCING_ARROW_L2 in ability_names
    assert ABILITY_BURNING_ARROW in ability_names


def test_burning_arrow_win_stores_delayed_effect():
    """When archer wins with burning arrow, no damage is dealt and delayed effect is stored."""
    game = get_debug_preset(PRESET_BURNING_ARROW_WIN)

    mage = game.players["player2"].characters[CHARACTER_MAGE]
    original_mage_health = mage.health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Mage should NOT take damage this turn
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == original_mage_health

    # Burning arrow effect should be stored on archer's character
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    burning_effect = f"{EFFECT_BURNING_ARROW}:player2:{CHARACTER_MAGE}"
    assert burning_effect in archer_after.effects


def test_burning_arrow_loss_deals_normal_damage_to_archer():
    """When archer loses with burning arrow active, archer takes normal damage and no burning effect is stored."""
    characters_p1 = init_characters(level=3)
    characters_p1[CHARACTER_ARCHER].active_abilities = [ABILITY_BURNING_ARROW]

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[1], result=BattleResult(winner=False, score=1)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    archer_before_health = game.players["player1"].characters[CHARACTER_ARCHER].health
    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Archer lost, takes normal damage
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert archer_after.health == archer_before_health - 1

    # Mage should NOT take any damage (mage won)
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health

    # No burning arrow effect stored (only stored on win)
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in archer_after.effects)


def test_burning_arrow_next_turn_applies_2_damage():
    """CharacterSelectAction applies 2 damage to target and clears burning arrow effect."""
    game = get_debug_preset(PRESET_BURNING_ARROW_NEXT_TURN)

    mage = game.players["player2"].characters[CHARACTER_MAGE]
    original_mage_health = mage.health

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(CHARACTER_ARCHER)

    # Mage should take 2 damage from burning arrow
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == original_mage_health - 2

    # Burning arrow effect should be cleared from archer
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in archer_after.effects)


def test_burning_arrow_next_turn_skip_turn_applies_2_damage():
    """SkipTurnAction also applies 2 damage when all characters are unavailable."""
    characters_p1 = init_characters(level=3)
    # Store burning arrow effect on archer
    characters_p1[CHARACTER_ARCHER].effects = [f"{EFFECT_BURNING_ARROW}:player2:{CHARACTER_MAGE}", EFFECT_SKIP_TURN]
    # Make all other characters unavailable
    characters_p1[CHARACTER_KNIGHT].health = 0
    characters_p1[CHARACTER_KNIGHT].is_alive = False
    characters_p1[CHARACTER_MAGE].health = 0
    characters_p1[CHARACTER_MAGE].is_alive = False

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = SkipTurnAction("player1", game)
    updated_game = action.run()

    # Mage should take 2 damage from burning arrow
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health - 2


def test_burning_arrow_dead_target_no_damage():
    """Burning arrow does not apply damage to a dead target character."""
    characters_p1 = init_characters(level=3)
    characters_p1[CHARACTER_ARCHER].effects = [f"{EFFECT_BURNING_ARROW}:player2:{CHARACTER_MAGE}"]

    characters_p2 = init_characters()
    # Target is already dead
    characters_p2[CHARACTER_MAGE].health = 0
    characters_p2[CHARACTER_MAGE].is_alive = False

    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(CHARACTER_ARCHER)

    # Dead mage should not be affected (health stays at 0)
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == 0
    assert mage_after.is_alive is False


def test_burning_arrow_causes_level_down():
    """Burning arrow 2-damage can trigger level-down on target at 1 HP."""
    characters_p1 = init_characters(level=3)
    characters_p1[CHARACTER_ARCHER].effects = [f"{EFFECT_BURNING_ARROW}:player2:{CHARACTER_MAGE}"]

    characters_p2 = init_characters(level=2)
    # Mage L2 at 1 HP — burning arrow will deal 2 damage, forcing level-down
    characters_p2[CHARACTER_MAGE].health = 1

    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(CHARACTER_ARCHER)

    # Mage L2 at 1 HP takes 2 damage → health=0 → level down to L1, restored to L1 max_health
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.level == 1
    assert mage_after.health == mage_after.max_health
    assert mage_after.is_alive is True


def test_burning_arrow_draw_no_delayed_effect():
    """In a draw, burning arrow active ability is cleared but no burning effect is stored."""
    characters_p1 = init_characters(level=3)
    characters_p1[CHARACTER_ARCHER].active_abilities = [ABILITY_BURNING_ARROW]

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[5], result=BattleResult(winner=False, score=5)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # No damage on draw
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health

    # No burning arrow effect stored (only on win)
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in archer_after.effects)
