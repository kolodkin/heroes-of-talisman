from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..common import GameException, ReportedException, ChatacterType
from ..effects import EFFECT_DRAIN
from ..gameplay import (
    StageName,
    STAGE_CHARACTER_SELECT,
    GamePlay,
    Player,
    Character,
    CHARACTER_STATS_BY_LEVEL,
    AbilityItemMeta,
    ActivePlayer1,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent2,
    Opponent3,
    Opponent4,
)


class Action(ABC):
    def __init__(self, user: str, game: GamePlay):
        self.user: str = user
        self.game: GamePlay = game

    # convenience helpers similar to GameEngine properties

    @property
    def stage(self) -> Optional[str]:
        return self.game.stage

    @stage.setter
    def stage(self, value: Optional[str]):
        self.game.stage = value

    @property
    def active(self) -> Optional[ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4]:
        return self.game.active

    @active.setter
    def active(self, value: Optional[ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4]):
        self.game.active = value

    @property
    def active_character(self) -> Character:
        """
        Get the active player's character card.

        Provides validation that active player exists and has a character selected.

        Raises:
            GameException: If active player is not set or has no character selected
        """
        if not self.active or not isinstance(self.active, (ActivePlayer2, ActivePlayer3, ActivePlayer4)):
            raise GameException("Active player not set or has no character selected")
        return self.game.players[self.active.player].characters[self.active.character]

    @property
    def players(self):
        return self.game.players

    @players.setter
    def players(self, value: dict[str, Player]):
        self.game.players = value

    @property
    def player(self) -> Player:
        if self.user not in self.players:
            raise GameException("Player not in game")
        return self.players[self.user]

    @property
    def stage_meta(self) -> Optional[Dict[str, Any]]:
        return self.game.stage_meta

    @stage_meta.setter
    def stage_meta(self, value: Optional[Dict[str, Any]]):
        self.game.stage_meta = value

    @property
    def opponent(self) -> Optional[Opponent2 | Opponent3 | Opponent4]:
        return self.game.opponent

    @opponent.setter
    def opponent(self, value: Optional[Opponent2 | Opponent3 | Opponent4]):
        self.game.opponent = value

    @property
    def ability_item_target_character(self) -> Character:
        """
        Get the target character for ability item selection.

        Provides validation that stage_meta is an AbilityItemMeta with valid target.

        Raises:
            GameException: If stage_meta is not set or is not an AbilityItemMeta
        """
        if not self.stage_meta or not isinstance(self.stage_meta, AbilityItemMeta):
            raise GameException("No ability item target set")
        return self.game.players[self.stage_meta.target_player].characters[self.stage_meta.target_character]

    @property
    def opponent_character(self) -> Character:
        """
        Get the opponent's character card.

        Provides validation that opponent exists and has a character selected.

        Raises:
            GameException: If opponent is not set or has no character selected
        """
        if not self.opponent or not isinstance(self.opponent, (Opponent2, Opponent3, Opponent4)):
            raise GameException("Opponent not set or has no character selected")
        return self.game.players[self.opponent.player].characters[self.opponent.character]

    @property
    @abstractmethod
    def action_stages(self) -> Optional[list[StageName]]:
        """
        Return list of valid stages for this action, or None if action works in any stage.

        Examples:
            return [CHARACTER_SELECT]  # Only works in character select stage
            return [BATTLE_DICE_ROLL, BATTLE_END]  # Works in multiple stages
            return None  # Works in any stage (e.g., connection actions)
        """

    def assert_stage(self):
        """Validate that the game is in the correct stage for this action."""
        if self.action_stages is None:
            # Action works in any stage
            return

        if self.stage not in self.action_stages:
            stages_str = ", ".join(self.action_stages)
            raise GameException(f"Cannot perform action in stage '{self.stage}'. Valid stages: {stages_str}")

    def run(self, *args, **kwargs) -> GamePlay:
        """Execute the action with automatic stage validation."""
        self.assert_stage()
        return self._run(*args, **kwargs)

    @abstractmethod
    def _run(self, *args, **kwargs) -> GamePlay:
        """Execute the action logic. Implemented by subclasses."""


def apply_damage_with_level_check(
    character: Character,
    character_type: ChatacterType,
    damage: int,
    winner_has_talisman: bool = False,
) -> None:
    """
    Apply damage to a character with level-based death mechanic.

    If character health drops to 0 or below:
    - If winner has talisman: Character dies regardless of level
    - At level 2+: Reduce level by 1 and restore health to new level's max_health
    - At level 1: Character dies (health stays at 0)
    """
    character.health = max(0, character.health - damage)

    if character.health <= 0:
        if winner_has_talisman:
            character.is_alive = False
        elif character.level > 1:
            new_level = character.level - 1
            level_stats = CHARACTER_STATS_BY_LEVEL.get(new_level, CHARACTER_STATS_BY_LEVEL[1])
            char_stats = level_stats[character_type]

            character.level = new_level
            character.max_health = char_stats["max_health"]
            character.dice = char_stats["dice"]
            character.attack = char_stats["attack"]
            character.health = character.max_health
        else:
            character.is_alive = False


def _return_drained_items(game: GamePlay) -> None:
    """Return all borrowed (drained) items to their original owners."""
    drain_prefix = EFFECT_DRAIN + ":"
    for player in game.players.values():
        for char in player.characters.values():
            drain_effects = [e for e in char.effects if e.startswith(drain_prefix)]
            for eff in drain_effects:
                # Parse drain:{player}:{character}:{card}
                parts = eff.split(":", 3)
                target_player = parts[1]
                target_character = parts[2]
                card_name = parts[3]

                # Remove borrowed card from the drainer's active_cards
                if card_name in char.active_cards:
                    char.active_cards.remove(card_name)

                # Return card to original owner (if they still exist and character is alive)
                if target_player in game.players:
                    target_char = game.players[target_player].characters.get(target_character)
                    if target_char and target_char.is_alive:
                        target_char.active_cards.append(card_name)

            # Clear drain effects
            char.effects = [e for e in char.effects if not e.startswith(drain_prefix)]


def rotate_to_next_player(game: GamePlay) -> None:
    """
    Rotate to the next player and reset game state for character selection.

    Clears battle state (opponent, card, ability), returns drained items,
    and transitions to CHARACTER_SELECT stage with the next player as active.

    Args:
        game: The GamePlay instance to modify in place.
    """
    # Return any drained items before rotating
    _return_drained_items(game)

    player_names = list(game.players.keys())
    current_idx = player_names.index(game.active.player)
    next_player = player_names[(current_idx + 1) % len(player_names)]

    game.active = ActivePlayer1(player=next_player)
    game.opponent = None
    game.card = None
    game.ability = None
    game.stage = STAGE_CHARACTER_SELECT
    game.stage_meta = None
