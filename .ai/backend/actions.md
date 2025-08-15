# Backend Actions

Checklist of actions implemented in the server's action layer and the
class responsible for handling each action.

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)
- [x] `character_select` – stage where the player chooses a character (`CharacterSelectAction`)
- [x] `character_selected` – confirm character selection and move to card draw (`CharacterSelectedAction`)
- [x] `card_draw` – prompt the player to draw a card (`CardDrawAction`)
- [x] `card_select` – resolve the drawn card and advance to skill use (`CardSelectAction`)
