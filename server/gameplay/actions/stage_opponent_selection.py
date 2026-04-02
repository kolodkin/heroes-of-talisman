"""
Opponent Selection Stage Actions

This module implements actions for the opponent selection stage:
- OpponentPressAction: Highlights selected opponent by setting stage_meta
- OpponentSelectAction: Confirms opponent selection, applies card and ability effects to opponent, and transitions to battle stage
"""

from .action import Action
from ..abilities import get_ability_effects
from ..cards import CARDS_MAP
from ..common import GameException, ReportedException
from ..effects import APPLY_TO_BATTLE_OPPONENT, EFFECT_MIND_READING
from ..gameplay import STAGE_BATTLE_DICE_ROLL, STAGE_OPPONENT_SELECTION, GamePlay, Opponent2


class OpponentPressAction(Action):
    """
    Action invoked when an opponent's character is clicked during opponent selection.

    Sets stage_meta to an Opponent object with the chosen opponent player and character,
    triggering a game_update that highlights the selected opponent in the UI.
    """

    @property
    def action_stages(self):
        return [STAGE_OPPONENT_SELECTION]

    def _run(self, opponent: str, character: str) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate opponent exists
        if opponent not in self.game.players:
            raise ReportedException(f"Opponent {opponent} not in game")

        # Validate opponent is not the current player
        if opponent == self.user:
            raise ReportedException("Cannot select yourself as opponent")

        # Validate character exists for opponent
        opponent_player = self.game.players[opponent]
        if character not in opponent_player.characters:
            raise ReportedException(
                f"Character {character} not available for opponent"
            )

        # Validate character is alive
        if not opponent_player.characters[character].is_alive:
            raise ReportedException(f"Opponent character {character} is dead and can't be selected")

        # Validate character is not protected by mind_reading against the active player
        mind_reading_protection = f"{EFFECT_MIND_READING}:{self.user}"
        if mind_reading_protection in opponent_player.characters[character].effects:
            raise ReportedException(f"Character {character} is protected by mind reading")

        # Set selected opponent in stage metadata
        self.game.stage_meta = Opponent2(player=opponent, character=character)

        return self.game


class OpponentSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm opponent choice.

    Reads the selected opponent from stage_meta, populates the opponent field
    in game metadata, and transitions the game stage to 'battle'.
    """

    @property
    def action_stages(self):
        return [STAGE_OPPONENT_SELECTION]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate stage_meta is set and is an Opponent2
        if not self.game.stage_meta or not isinstance(
            self.game.stage_meta, Opponent2
        ):
            raise ReportedException("No opponent selected")

        # Get opponent from stage_meta
        selected_opponent = self.game.stage_meta

        # Validate opponent character is still alive
        opponent_player = self.game.players[selected_opponent.player]
        opponent_character = opponent_player.characters[selected_opponent.character]
        if not opponent_character.is_alive:
            raise ReportedException(
                f"Opponent character {selected_opponent.character} is dead and can't be selected"
            )

        # Validate character is not protected by mind_reading against the active player
        mind_reading_protection = f"{EFFECT_MIND_READING}:{self.user}"
        if mind_reading_protection in opponent_character.effects:
            raise ReportedException(f"Character {selected_opponent.character} is protected by mind reading")

        # Set opponent in game metadata
        self.game.opponent = selected_opponent

        # Apply "battle_opponent" effects from card to the opponent's character
        if self.game.card:
            card_obj = CARDS_MAP.get(self.game.card)
            if card_obj:
                for effect in card_obj.effects:
                    if effect.apply_to == APPLY_TO_BATTLE_OPPONENT:
                        opponent_character.effects.append(effect.name)

        # Apply "battle_opponent" effects from ability to the opponent's character
        # Store ability name (not effect name) to preserve value info for lookup in Character.effect
        if self.game.ability:
            has_battle_opponent_effect = any(
                effect.apply_to == APPLY_TO_BATTLE_OPPONENT
                for effect in get_ability_effects(self.game.ability)
            )
            if has_battle_opponent_effect:
                opponent_character.effects.append(self.game.ability)

        # Transition to battle dice roll stage
        self.game.stage = STAGE_BATTLE_DICE_ROLL
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
