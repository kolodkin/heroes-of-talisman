# Technical Debt

## Action Base Class — Missing `stage_meta` Accessor Properties

**Context:** `Action` base class (`server/gameplay/actions/action.py`) provides typed properties that
wrap nested `game` state access (e.g. `active_character`, `opponent_character`,
`ability_item_target_character`). This avoids raw `self.game.X.Y.Z` chains in subclasses and
centralises validation.

Several `stage_meta` fields are still accessed directly in action subclasses and should get the
same treatment.

---

### 1. `ability_item_selected_item` — selected item during Dragon Breath item selection

**Missing property:**

```python
@property
def ability_item_selected_item(self) -> str:
    if not self.stage_meta or not isinstance(self.stage_meta, AbilityItemMeta):
        raise GameException("No ability item target set")
    if not self.stage_meta.selected_item:
        raise ReportedException("No item selected")
    return self.stage_meta.selected_item
```

**Current direct access in:** `server/gameplay/actions/stage_ability_item_selection.py`

- Line 69: `if not self.game.stage_meta.selected_item:`
- Line 72: `selected_item = self.game.stage_meta.selected_item`

---

### 2. `drawn_card` — card drawn during card draw stage

**Missing property:**

```python
@property
def drawn_card(self) -> str:
    if not self.stage_meta or not isinstance(self.stage_meta, CardDrawMeta):
        raise GameException("No drawn card in stage metadata")
    return self.stage_meta.drawn_card
```

**Current direct access in:** `server/gameplay/actions/stage_card_draw.py`

- Line 81: `drawn_card_name = self.game.stage_meta.drawn_card`

---

### 3. `selected_opponent_meta` — opponent highlighted during opponent/ability-opponent selection

Both `OpponentSelectAction` and `AbilityOpponentSelectAction` read the full `Opponent2` object
from `stage_meta` after validating it. A shared property would deduplicate this and add
consistent validation.

**Missing property:**

```python
@property
def selected_opponent_meta(self) -> Opponent2:
    if not self.stage_meta or not isinstance(self.stage_meta, Opponent2):
        raise ReportedException("No opponent selected")
    return self.stage_meta
```

**Current direct access in:**

- `server/gameplay/actions/stage_opponent_selection.py` line 91: `selected_opponent = self.game.stage_meta`
- `server/gameplay/actions/stage_ability_opponent_selection.py` line 101: `selected_opponent = self.game.stage_meta`

---

## GitHub Actions — Forced Node.js 24 via Environment Variable

**Context:** Several actions (`actions/checkout@v4`, `astral-sh/setup-uv@v6`, etc.) still run on
Node.js 20, which GitHub has deprecated. There is no Node.js 22/24 release of these actions yet.

As a workaround, `.github/workflows/ci.yml` sets:

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_RUNNER_NODE_VERSION: node24
```

**Resolution:** Once upstream actions publish Node.js 24-based releases, remove this env var and
pin to the updated action versions instead.
