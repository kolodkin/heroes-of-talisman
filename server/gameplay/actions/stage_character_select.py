"""
Character Select Stage Actions

This module implements actions for the character selection stage:
- CharacterPressAction: Highlights selected character by setting stage_meta
- CharacterSelectAction: Confirms selection, disposes effects, and transitions to card_draw
- SkipTurnAction: Skips turn when no character is available (all dead or have skip_turn effect)
"""

from .action import Action, apply_damage_with_level_check, rotate_to_next_player
from ..common import (
    GameException,
    ReportedException,
)
from ..effects import EFFECT_BURNING_ARROW, EFFECT_DRAIN, EFFECT_MIND_READING
from ..gameplay import (
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    STAGE_CHARACTER_SELECT,
    GamePlay,
    CharacterSelectMeta,
    CardDrawMeta,
    AbilitySelectMeta,
    ActivePlayer2,
)


def _decrement_burning_arrow(eff: str, char_type: str, char) -> str | None:
    """Decrement a burning_arrow:N effect. Returns updated effect string, or None if it fired."""
    count = int(eff.split(":")[1]) - 1
    if count <= 0:
        if char.is_alive:
            apply_damage_with_level_check(char, char_type, 2)
        return None
    return f"{EFFECT_BURNING_ARROW}:{count}"


def _clear_mind_reading_for_player(game: GamePlay, player_name: str) -> None:
    """Clear mind_reading:{player_name} effects from ALL characters across ALL players."""
    prefix = f"{EFFECT_MIND_READING}:{player_name}"
    for player in game.players.values():
        for char in player.characters.values():
            char.effects = [e for e in char.effects if e != prefix]


def _process_burning_arrow_effects(game: GamePlay) -> None:
    """Decrement burning_arrow countdowns on ALL characters. Apply 2 damage when count reaches 0."""
    prefix = EFFECT_BURNING_ARROW + ":"
    for player in game.players.values():
        for char_type, char in player.characters.items():
            char.effects = [
                result
                for eff in char.effects
                for result in [_decrement_burning_arrow(eff, char_type, char) if eff.startswith(prefix) else eff]
                if result is not None
            ]


class CharacterPressAction(Action):
    """
    Action invoked when a character is clicked during character selection.

    Sets stage_meta['selected'] to the chosen character name, triggering
    a game_update that highlights the selected character in the UI.
    """

    @property
    def action_stages(self):
        return [STAGE_CHARACTER_SELECT]

    def _run(self, character: str) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate character exists for this player
        player = self.game.players[self.user]
        if character not in player.characters:
            raise ReportedException(f"Character {character} not available")

        # Validate character is alive
        if not player.characters[character].is_alive:
            raise ReportedException(f"Character {character} is dead and can't be selected")

        # Set selected character in stage metadata
        self.game.stage_meta = CharacterSelectMeta(selected=character)

        return self.game


class CharacterSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm character choice.

    Populates selected_character in game metadata, clears skip_turn effects,
    and transitions the game stage to 'card_draw'.
    """

    @property
    def action_stages(self):
        return [STAGE_CHARACTER_SELECT]

    def _run(self, character: str) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate character exists for this player
        player = self.game.players[self.user]
        if character not in player.characters:
            raise ReportedException(f"Character {character} not available")

        # Validate character is alive
        if not player.characters[character].is_alive:
            raise ReportedException(f"Character {character} is dead and can't be selected")

        # Clear mind_reading protection that targeted this player
        _clear_mind_reading_for_player(self.game, self.user)

        # Decrement burning arrow countdowns across all characters, fire if count reaches 0
        _process_burning_arrow_effects(self.game)

        # Clear effects (e.g., skip_turn) from active player's characters, preserving persistent effects
        persistent_prefixes = (EFFECT_BURNING_ARROW + ":", EFFECT_DRAIN + ":", EFFECT_MIND_READING + ":")
        for char in player.characters.values():
            char.effects = [e for e in char.effects if e.startswith(persistent_prefixes)]

        # Update active player with selected character
        self.game.active = ActivePlayer2(player=self.user, character=character)

        # Transition to card_draw stage
        self.game.stage = STAGE_CARD_DRAW

        # Clear stage_meta - will be populated by CardDrawAction
        self.game.stage_meta = None

        return self.game


class SkipTurnAction(Action):
    """
    Action invoked when no character is available for selection.

    This happens when all characters are either dead (health=0) or have
    a skip_turn effect. The turn is skipped and passes to the next player.

    Clears skip_turn effects and transitions to the next player's
    character_select stage.
    """

    @property
    def action_stages(self):
        return [STAGE_CHARACTER_SELECT]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        player = self.game.players[self.user]

        # Validate that no character is available
        available_characters = [
            char_name for char_name, char in player.characters.items()
            if char.is_available
        ]

        if available_characters:
            raise ReportedException(
                "Cannot skip turn: available characters exist"
            )

        # Clear mind_reading protection that targeted this player
        _clear_mind_reading_for_player(self.game, self.user)

        # Decrement burning arrow countdowns across all characters, fire if count reaches 0
        _process_burning_arrow_effects(self.game)

        # Clear effects (e.g., skip_turn) from active player's characters, preserving persistent effects
        persistent_prefixes = (EFFECT_BURNING_ARROW + ":", EFFECT_DRAIN + ":", EFFECT_MIND_READING + ":")
        for char in player.characters.values():
            char.effects = [e for e in char.effects if e.startswith(persistent_prefixes)]

        # Rotate to next player's turn
        rotate_to_next_player(self.game)

        return self.game
