## Game Play

This document outlines the gameplay architecture and component hierarchy for the game engine, detailing main components.

- [FrontEnd GamePlay](/docs/gameplay_frontend.md)
- [BackEnd GamePlay](/docs/gameplay_backend.md)

# Overview

This engine offers a fully integrated backend and frontend interaction system, supporting multiple players with their characters and a shared area.
It is built on a tightly integrated system of React components and Pydantic models, with data exchanged via JSON serialization.

The game supports internationalization via react-i18next, currently configured for Hebrew only.

## Game Requirements

- **Minimum Players**: At least 2 players are required for the game to start
- Players do not need to be connected, but at least 2 players must have joined the game

# Backend Alignment

Frontend components are designed to work seamlessly with the backend models outlined in [gameplay backend](/docs/gameplay_backend.md).

# Core Architecture

## Game Board Structure

The engine expects a JSON game board as defined in backend "server/gameplay/models.py -> GameBoard"

# Component\Models Hierarchy

## Navbar

- Game name
- Username
- Current stage name (translated)
- Current playing player

## GameBoard

- Manages overall game state
- Handles player turns and game flow
- Coordinates between all child components
- Manages SharedArea and Players

## SharedArea

- Common game elements
- Displays stage-specific UI components

## Player

- The status and characters for a single player
- Holds player connection status (connected/disconnected)

# Interactive

Any player action that updates the gameplay state will trigger an update for all players in the game via the WebSocket connection. This update implicitly causes a re-render of the game UI for all connected players, ensuring synchronized game state across all clients.

# Characters

The game features three distinct character types:

- **Knight**: Has the strongest attack skills and health
- **Archer**: Has the highest health
- **Mage**: Has the strongest special skills

## Character Levels

Characters can progress through levels, gaining improved stats at higher levels.

| Character | Level | Max Health | Dice | Attack |
| --------- | ----- | ---------- | ---- | ------ |
| Knight    | 1     | 2          | 1    | 1      |
| Knight    | 2     | 3          | 1    | 3      |
| Knight    | 3     | 4          | 2    | 1      |
| Knight    | 4     | 5          | 2    | 3      |
| Archer    | 1     | 3          | 1    | 0      |
| Archer    | 2     | 4          | 1    | 2      |
| Archer    | 3     | 5          | 2    | 0      |
| Archer    | 4     | 6          | 2    | 1      |
| Mage      | 1     | 2          | 1    | 0      |
| Mage      | 2     | 3          | 1    | 2      |
| Mage      | 3     | 4          | 2    | 0      |
| Mage      | 4     | 5          | 2    | 1      |

### Level Progression

- **Leveling Up**: Characters level up when using the Magic Ball card. Upon leveling up, health is restored to the new max health.
- **Leveling Down**: When a character at level 2+ drops to 0 health, they lose one level instead of dying. Their stats are reduced to the lower level and health is restored to the new max health.

## Lifespan

A character dies only when their health hits 0 while at **level 1**. Characters at level 2 or higher will instead lose a level and have their health restored (see Level Progression above). **Exception**: If the winning character holds a **Talisman**, the defeated opponent dies regardless of their level. A dead character can no longer be selected neither as an active player character nor as an opponent.

# Abilities & Effects

Each character has abilities that trigger effects (attack bonus, skip turn, reroll dice) targeting self, battle opponent, or a selected opponent. Effects persist until disposed by specific game actions.

See [Backend GamePlay - Abilities & Effects](/docs/gameplay_backend.md#abilities--effects) for the abilities table and implementation details.

# Cards

Cards are drawn from a shared deck (auto-reset when empty) after character selection. Restricted characters cannot use certain cards.

| Card            | Type       | Effect                                                             | Restrictions |
| --------------- | ---------- | ------------------------------------------------------------------ | ------------ |
| `metal_armor`   | Equipment  | +2 defense bonus (persistent)                                      | None         |
| `sacred_sword`  | Equipment  | +3 attack bonus (persistent)                                       | Archer       |
| `golden_apple`  | Instant    | +1 heal (capped at max health)                                     | None         |
| `magic_ball`    | Instant    | +1 level up, restores health to new max                            | None         |
| `devils_fork`   | Instant    | -1 level down, no effect at level 1                                | None         |
| `darkness_rise` | Instant    | Skip turn for all alive characters above level 1 (all players)     | None         |
| `talisman`      | Persistent | Kills defeated opponent regardless of level (overrides level-down) | None         |

**Types:** Equipment = persistent stat bonus, Instant = applied immediately then discarded, Persistent = ongoing passive effect.

# Game Stages

The game progresses through distinct stages during each player's turn. Upon completing all stages, the turn passes to the next player.

## Turn Stages

1. **Character Select** (`character_select`) - Player chooses which character will act during this turn. If no character is available (all dead or have skip turn effect), the player must skip their turn.
2. **Card Draw** (`card_draw`) - Player draws a card from the deck and decides whether to keep it
3. **Ability Selection** (`ability_selection`) - Player selects which ability to use from the character's available abilities
4. **Ability Opponent Selection** (`ability_opponent_selection`) - _(Only for effects requiring target selection, e.g., SkipTurnEffect)_ Player selects an opponent character to apply the ability to
5. **Opponent Selection** (`opponent_selection`) - Player selects an opponent and one of the opponent's characters for battle
6. **Battle Dice Roll** (`battle_dice_roll`) - Both players roll dice for combat. Battle score = `sum(dice_roll) + attack + attack_bonus + attack_neg_bonus - opponent_defense_bonus`
7. **Battle End** (`battle_end`) - Combat results (damage) are applied to the loser
