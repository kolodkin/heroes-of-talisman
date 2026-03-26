"""
Tests for Archer Level 3 skills:
  1. bouncing_arrow_l3 (חץ קופץ) — same behavior as Archer L2
  2. burning_arrow (חץ בוער) — no damage this turn, 2 damage to target after 2 turn starts

Burning Arrow flow:
  1. Archer L3 selects burning_arrow ability
  2. Archer wins battle → burning_arrow:2 stored on OPPONENT's character (for visualization)
  3. Archer loses battle → normal loss damage to archer, no burning effect stored
  4. Opponent's turn start (CharacterSelectAction/SkipTurnAction) → burning_arrow:2 → burning_arrow:1
  5. Archer's next turn start → burning_arrow:1 → 0 → 2 damage applied to opponent character, effect cleared
"""

from .battle_end import BattleEndAction
from .stage_character_select import CharacterSelectAction, SkipTurnAction
from ..common import CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE
from ..abilities import ABILITY_BOUNCING_ARROW_L3, ABILITY_BURNING_ARROW
from ..effects import EFFECT_BURNING_ARROW, EFFECT_SKIP_TURN
from ..gameplay import (
    STAGE_BATTLE_END,
    STAGE_CHARACTER_SELECT,
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
    assert ABILITY_BOUNCING_ARROW_L3 in ability_names
    assert ABILITY_BURNING_ARROW in ability_names


def test_archer_l3_ability_selection_preset():
    """Archer L3 ability selection preset has correct setup with two abilities."""
    game = get_debug_preset(PRESET_ABILITY_SELECTION_ARCHER_L3)
    archer = game.players["player1"].characters[CHARACTER_ARCHER]
    ability_names = [a.name for a in archer.abilities]
    assert ABILITY_BOUNCING_ARROW_L3 in ability_names
    assert ABILITY_BURNING_ARROW in ability_names


def test_burning_arrow_win_stores_countdown_on_opponent():
    """When archer wins with burning arrow, no damage is dealt and burning_arrow:2 is stored on opponent's character."""
    game = get_debug_preset(PRESET_BURNING_ARROW_WIN)

    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Mage should NOT take damage this turn
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health

    # Countdown stored on the opponent's (mage's) character
    assert f"{EFFECT_BURNING_ARROW}:2" in mage_after.effects

    # Archer's effects should be clean
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in archer_after.effects)


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

    # Mage should NOT take any damage (mage won), and no burning arrow stored
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in mage_after.effects)


def test_burning_arrow_countdown_decrements_on_turn_start():
    """burning_arrow:2 on opponent's character decrements to burning_arrow:1 when any player starts their turn."""
    characters_p1 = init_characters(level=3)

    characters_p2 = init_characters()
    characters_p2[CHARACTER_MAGE].effects = [f"{EFFECT_BURNING_ARROW}:2"]

    game = GamePlay(
        stage=STAGE_CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(CHARACTER_ARCHER)

    # Mage health unchanged — arrow has not fired yet
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health

    # Countdown decremented to 1
    assert f"{EFFECT_BURNING_ARROW}:1" in mage_after.effects
    assert f"{EFFECT_BURNING_ARROW}:2" not in mage_after.effects


def test_burning_arrow_fires_after_two_turn_starts():
    """burning_arrow:1 fires on the next turn start, applying 2 damage."""
    game = get_debug_preset(PRESET_BURNING_ARROW_NEXT_TURN)

    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = CharacterSelectAction("player1", game)
    updated_game = action.run(CHARACTER_ARCHER)

    # Mage takes 2 damage
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health - 2

    # Burning arrow effect consumed
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in mage_after.effects)


def test_burning_arrow_skip_turn_also_decrements():
    """SkipTurnAction also decrements burning arrow countdown."""
    characters_p1 = init_characters(level=3)
    # All p1 chars unavailable
    characters_p1[CHARACTER_ARCHER].effects = [EFFECT_SKIP_TURN]
    characters_p1[CHARACTER_KNIGHT].health = 0
    characters_p1[CHARACTER_KNIGHT].is_alive = False
    characters_p1[CHARACTER_MAGE].health = 0
    characters_p1[CHARACTER_MAGE].is_alive = False

    characters_p2 = init_characters()
    characters_p2[CHARACTER_MAGE].effects = [f"{EFFECT_BURNING_ARROW}:1"]

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

    # Mage takes 2 damage when burning_arrow:1 fires
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health - 2
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in mage_after.effects)


def test_burning_arrow_dead_target_not_damaged():
    """Burning arrow does not apply damage to a dead target character."""
    characters_p1 = init_characters(level=3)

    characters_p2 = init_characters()
    characters_p2[CHARACTER_MAGE].health = 0
    characters_p2[CHARACTER_MAGE].is_alive = False
    characters_p2[CHARACTER_MAGE].effects = [f"{EFFECT_BURNING_ARROW}:1"]

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

    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == 0
    assert mage_after.is_alive is False


def test_burning_arrow_causes_level_down():
    """Burning arrow 2-damage can trigger level-down on target at 1 HP."""
    characters_p1 = init_characters(level=3)

    characters_p2 = init_characters(level=2)
    characters_p2[CHARACTER_MAGE].health = 1
    characters_p2[CHARACTER_MAGE].effects = [f"{EFFECT_BURNING_ARROW}:1"]

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

    # Mage L2 at 1 HP takes 2 damage → level down to L1, restored to L1 max_health
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.level == 1
    assert mage_after.health == mage_after.max_health
    assert mage_after.is_alive is True


def test_burning_arrow_draw_no_delayed_effect():
    """In a draw, burning arrow active ability is cleared but no countdown is stored."""
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

    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health
    assert not any(e.startswith(EFFECT_BURNING_ARROW + ":") for e in mage_after.effects)
