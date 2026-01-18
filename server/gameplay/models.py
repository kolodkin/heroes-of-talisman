"""
Backwards compatibility - re-exports from split modules.
Import directly from effects, abilities, or gameplay for new code.
"""

# Re-export from effects
from .effects import (
    Effect,
    SkipTurnEffect,
    AttackBonusEffect,
    RerollDiceEffect,
    AttackNegBonusEffect,
    DrawCardEffect,
    EffectUnion,
    EffectTotal,
)

# Re-export from abilities
from .abilities import (
    Ability,
    ABILITIES_MAP,
)

# Re-export from gameplay (everything else)
from .gameplay import (
    # Connection statuses
    CONNECTED,
    DISCONNECTED,
    CONNECTION_STATUSES,
    ConnectionStatus,
    # Stages
    CHARACTER_SELECT,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    BATTLE_DICE_ROLL,
    BATTLE_END,
    STAGES_NAMES,
    StageName,
    # Character types
    KNIGHT,
    ARCHER,
    MAGE,
    CHARACTER_TYPES,
    ChatacterType,
    # Ability names
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
    ABILITIES_NAMES,
    AbilityName,
    # Effect names
    ATTACK_BONUS,
    ATTACK_NEG_BONUS,
    REROLL_DICE,
    SKIP_TURN,
    DRAW_CARD,
    # Apply to targets
    APPLY_TO_SELF,
    APPLY_TO_BATTLE_OPPONENT,
    APPLY_TO_SELECTED_OPPONENT,
    APPLY_TO_TARGETS,
    ApplyToTarget,
    # Effect source map
    EFFECTS_SOURCE_ABILITY_MAP,
    # Actions
    CONNECT,
    LEAVE,
    DISCONNECT,
    CHARACTER_PRESS,
    CHARACTER_SELECT_ACTION,
    ABILITY_PRESS,
    ABILITY_SELECT,
    ABILITY_OPPONENT_PRESS,
    ABILITY_OPPONENT_SELECT,
    OPPONENT_PRESS,
    OPPONENT_SELECT,
    ACTIVE_PLAYER_ROLL,
    OPPONENT_ROLL,
    ACTION_REROLL,
    ACTION_REROLL_EFFECT,
    BATTLE_END_ACTION,
    DEBUG_SET_BATTLE_DICE_ROLLS,
    ACTION_NAMES,
    ActionName,
    # Exceptions
    GameException,
    ReportedException,
    # Utilities
    recursive_db_model_dump,
    StrictModel,
    # Character and game models
    Character,
    CharacterSelectMeta,
    AbilitySelectMeta,
    ActivePlayer1,
    BattleResult,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    ActivePlayer,
    Opponent2,
    Opponent3,
    Opponent4,
    Opponent,
    Player,
    GamePlay,
    DEFAULT_GAME,
    # Character default stats
    KNIGHT_L1_DEFAULT_HEALTH,
    KNIGHT_L1_MAX_HEALTH,
    KNIGHT_L1_DICE,
    KNIGHT_L1_ATTACK,
    KNIGHT_L1_ABILITY,
    ARCHER_L1_DEFAULT_HEALTH,
    ARCHER_L1_MAX_HEALTH,
    ARCHER_L1_DICE,
    ARCHER_L1_ATTACK,
    ARCHER_L1_ABILITY,
    MAGE_L1_DEFAULT_HEALTH,
    MAGE_L1_MAX_HEALTH,
    MAGE_L1_DICE,
    MAGE_L1_ATTACK,
    MAGE_L1_ABILITY,
    CHARACTER_DEFAULT_STATS,
    init_characters,
)
