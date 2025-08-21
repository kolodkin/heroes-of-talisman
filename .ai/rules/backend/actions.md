# Server Action Design

The server's action layer organizes game mutations into small, focused
classes. Each action is invoked with the current user and `GameModel`
state and returns the updated game after running.

## Core Components

- **`Action` base class**: provides convenience accessors for game
  properties (players, stage, deck) and the `assert_stage` helper to
  validate that an action is executed in the correct phase.
- **Connection actions** (`ConnectAction`, `LeaveAction`,
  `DisconnectAction`): manage player lifecycle by connecting players,
  removing them from the game, or marking them as disconnected.
- **Character actions** (`CharacterSelectAction`, `CharacterSelectedAction`):
  handle the character selection phase and transition the game into the
  card draw phase once a character is chosen.
- **Card actions** (`CardDrawAction`, `CardSelectAction`): control drawing
  and selecting cards, maintaining the deck and moving play into the
  skill usage stage.
- **Models**: Pydantic models (`GameModel`, `PlayerModel`, `CharacterModel`)
  describe the game state and enforce structure and types.

## Workflow

1. An action instance is created with a user identifier and the current
   `GameModel`.
2. The client-provided parameters are passed to the action's `run`
   method.
3. The action updates the `GameModel` and returns it for broadcasting to
   other players.

## Error Handling

- `GameException` represents general server-side errors.
- `ReportedException` indicates errors that should be surfaced to the
  client, such as invalid stages or missing resources.

## Extending Actions

To implement a new action, subclass `Action` and implement the `run`
method. Use `assert_stage` to ensure the action only executes during the
appropriate game phase and update the `GameModel` as needed.

# Server Actions

Checklist of actions implemented in the server's action layer and the
class responsible for handling each action.

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)
