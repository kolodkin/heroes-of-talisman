"""
Battle End Action

Ends the battle, calculates winner, and reduces loser's health by 1.
At level 2+, dropping to 0 health reduces level instead of dying.
At level 1, dropping to 0 health means the character dies.
"""

from .action import Action, apply_damage_with_level_check, rotate_to_next_player
from ..common import GameException, ReportedException
from ..abilities import ABILITY_BURNING_ARROW
from ..effects import EFFECT_NO_DAMAGE_ON_WIN, EFFECT_BURNING_ARROW
from ..gameplay import (
    STAGE_BATTLE_END,
    GamePlay,
    ActivePlayer3,
    ActivePlayer4,
    Opponent3,
    Opponent4,
)


class BattleEndAction(Action):
    """
    Action invoked when the active player presses continue after battle.

    Calculates the winner based on dice + attack values, reduces loser's health by 1,
    clears battle state, and transitions to character_select stage.
    """

    @property
    def action_stages(self):
        return [STAGE_BATTLE_END]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate both players have rolled (must be ActivePlayer3/4 and Opponent3/4)
        if not isinstance(self.game.active, (ActivePlayer3, ActivePlayer4)) or not self.game.active.dice_roll:
            raise ReportedException("Active player hasn't rolled yet")

        if not self.game.opponent or not isinstance(self.game.opponent, (Opponent3, Opponent4)) or not self.game.opponent.dice_roll:
            raise ReportedException("Opponent hasn't rolled yet")

        # Get characters using properties
        active_character = self.active_character
        opponent_character = self.opponent_character

        # Use scores already calculated by calculate_winner in the dice roll stage
        active_score = self.game.active.result.score
        opponent_score = self.game.opponent.result.score

        # Determine loser and reduce health by 1
        has_burning_arrow = ABILITY_BURNING_ARROW in active_character.active_abilities

        if active_score > opponent_score:
            # Active player wins
            if has_burning_arrow:
                # Burning arrow: store countdown on opponent's character for visualization
                opponent_character.effects.append(f"{EFFECT_BURNING_ARROW}:2")
            elif not active_character.effect.no_damage_on_win:
                apply_damage_with_level_check(
                    opponent_character,
                    self.game.opponent.character,
                    1,
                    winner_has_talisman=active_character.effect.has_talisman,
                )
        elif opponent_score > active_score:
            # Opponent wins, active player loses health
            apply_damage_with_level_check(
                active_character,
                self.game.active.character,
                1,
                winner_has_talisman=opponent_character.effect.has_talisman,
            )
        # If tied, no one loses health

        # Clear active abilities from both characters at battle end
        active_character.active_abilities = []
        opponent_character.active_abilities = []

        # Clear no_damage_on_win effect from active character
        if EFFECT_NO_DAMAGE_ON_WIN in active_character.effects:
            active_character.effects.remove(EFFECT_NO_DAMAGE_ON_WIN)

        # Rotate to next player's turn
        rotate_to_next_player(self.game)

        return self.game
