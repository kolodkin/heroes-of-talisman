from typing import Literal, Optional

from .models import GamePlay, DEFAULT_GAME, STAGES_NAMES

HEALTH_1 = "health_1"
DEBUG_PRESETS = Literal["default", "health_1"]


def set_health_1(game: GamePlay) -> GamePlay:
    ret = game.model_copy(deep=True)
    for player in ret.players.values():
        for character in player.characters.values():
            character.health = 1
    return ret


def get_debug_preset(preset: DEBUG_PRESETS, stage: Optional[STAGES_NAMES] = None) -> GamePlay:
    if preset == "default":
        ret = DEFAULT_GAME.model_copy(deep=True)
    elif preset == "health_1":
        ret = set_health_1(DEFAULT_GAME)
    else:
        raise ValueError(f"Invalid preset: {preset}")

    if stage is not None:
        ret.stage = stage

    return ret
