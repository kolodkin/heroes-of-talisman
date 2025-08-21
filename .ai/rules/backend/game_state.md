# Game State Modeling

- Use the following Pydantic models to represent the game state (see `server/actions/models.py`):
  - `GameModel`: Represents the entire current state of the game.
  - `PlayerModel`: Represents the state of an individual player.
  - `CharacterModel`: Represents the stats and attributes of a player's character.

- There are three character types available in the game:
  - Knight
  - Archer
  - Mage

- Default stats for each character type are defined in the `CHARACTER_DEFAULT_STATS` dictionary.
