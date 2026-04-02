# Future Improvements

## Game Deleted Indication

When a game is deleted while players are connected, the server sends a generic "Game not found" error. The client handles this by showing an error toast and redirecting to the home page, but the message is unclear — it doesn't distinguish between a game that never existed and one that was actively deleted.

**Improvement:** Send a distinct `"Game deleted"` event so the client can show a specific message like "This game has been deleted" instead of "Game not found".

## Energy Mist — Mage Level 3 Ability

`energy_mist` (ערפל אנרגיה): All targeted ability effects and all card effects in the next 2 full round-robins affect all alive characters of all players (including self).

### Design Notes

- **Scope**: All abilities that target a single opponent → apply to all alive characters. All card effects (instant, equipment, persistent) → apply to all alive characters of all players.
- **Duration**: 2 full round-robins (every player takes a turn = 1 round). Tracked via `energy_mist:2` → `energy_mist:1` strings on the mage character + a dedicated `energy_mist` field on the `GamePlay` model.
- **Stacking**: Only one active energy mist at a time. A new activation replaces the existing one.
- **Equipment cards under energy mist**: All characters temporarily gain the effect of equipment cards drawn during energy mist (implementation: check energy_mist flag in relevant places rather than duplicating cards to all characters).
- **Complexity**: Deferred due to the broad cross-cutting nature — requires intercepting ability targeting, card draw effects, and turn rotation logic.
