# Image Map

This document maps game entity names to their corresponding image files.

## Abilities

Images are loaded dynamically in `AbilityCard.jsx` as `/images/effects/{ability.name}.jpg`.

> **Note:** The folder is named `effects/` but contains ability images. Consider renaming to `abilities/` for clarity, since "effects" in the codebase refers to the game mechanic types (`AttackBonusEffect`, `RerollDiceEffect`, etc.), not abilities.

| Ability Name | Image File | Hebrew Name |
|---|---|---|
| `battle_howl` | `public/images/effects/battle_howl.jpg` | שאגת קרב |
| `bouncing_arrow` | `public/images/effects/bouncing_arrow.jpg` | חץ מקפץ |
| `bouncing_arrow_l2` | `public/images/effects/bouncing_arrow_l2.jpg` | חץ קופץ |
| `freeze` | `public/images/effects/freeze.jpg` | הקפאה |
| `disarm` | `public/images/effects/disarm.jpg` | פריקת נשק |

### Unassigned Images in `effects/`

| Image File | Notes |
|---|---|
| `public/images/effects/storm.jpg` | No matching ability defined |

## Characters

Images are loaded dynamically in `CharacterCard.jsx` as `/images/{name}.png`.

| Character Name | Image File | Hebrew Name |
|---|---|---|
| `knight` | `public/images/knight.png` | אביר |
| `archer` | `public/images/archer.png` | קשת |
| `mage` | `public/images/mage.png` | קוסם |

## Cards

Images are loaded dynamically in `GameplayCard.jsx` as `/images/cards/{cardName}.png`.

| Card Name | Image File | Hebrew Name |
|---|---|---|
| `metal_armor` | `public/images/cards/metal_armor.png` | שריון מתכת |
| `sacred_sord` | `public/images/cards/sacred_sord.png` | חרב קדושה |
| `golden_apple` | `public/images/cards/golden_apple.png` | תפוח זהב |
| `magic_ball` | `public/images/cards/magic_ball.png` | כדור קסם |
| `devils_fork` | `public/images/cards/devils_fork.png` | קלשון השטן |
| `darkness_rise` | `public/images/cards/darkness_rise.png` | עליית חושך |
| `talisman` | `public/images/cards/talisman.png` | קמע |
| `fog` | `public/images/cards/fog.png` | ערפל |
