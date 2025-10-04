# Backend Action Design

The backend action layer organizes game mutations into small, focused
classes. Each action is invoked with the current user and `GamePlay`
state and returns the updated game after running.

## Core Components

- **`Action` base class**: provides convenience accessors for game
  properties (players, stage, deck) and the `assert_stage` helper to
  validate that an action is executed in the correct phase.
- **Connection actions** (`ConnectAction`, `LeaveAction`,
  `DisconnectAction`): manage player lifecycle by connecting players,
  removing them from the game, or marking them as disconnected.
- **Models**: Pydantic models (`GamePlay`, `Player`, `CharacterCard`)
  describe the game state and enforce structure and types.

## Stage: Character Select

The character selection stage allows players to choose which character
will act during their turn.

- **`CharacterPressAction`**: Sets `stage_meta['selected']` to the
  character name pressed by the active player. Validates that the player
  is active, the stage is `character_select`, and the character exists
  for this player.
- **`CharacterSelectAction`**: Confirms the character selection by
  setting `selected_character` to the chosen character name and
  transitioning the game stage from `character_select` to `battle`.
  Clears `stage_meta` after transition.

## Workflow

1. An action instance is created with a user identifier and the current
   `GamePlay`.
2. The client-provided parameters are passed to the action's `run`
   method.
3. The action updates the `GamePlay` and returns it for broadcasting to
   other players.

## Error Handling

- `GameException` represents general server-side errors.
- `ReportedException` indicates errors that should be surfaced to the
  client, such as invalid stages or missing resources.

## Extending Actions

To implement a new action, subclass `Action` and implement the `run`
method. Use `assert_stage` to ensure the action only executes during the
appropriate game phase and update the `GamePlay` as needed.

# Backend Actions

Checklist of actions implemented in the server's action layer and the
class responsible for handling each action.

## General

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)

## Charachter Select Stage

- [x] `character_press` – highlight selected character in (`CharacterPressAction`)
- [x] `character_select` – confirm character selection and transition to battle (`CharacterSelectAction`)
