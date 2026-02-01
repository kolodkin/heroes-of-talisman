import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  he: {
    translation: {
      direction: "rtl",
      game_name: "Heroes of Talisman",
      disconnected: "התנתק",
      nav: {
        playing: "משחק",
      },
      home: {
        notify_empty: "אנא הזן שם",
      },
      shared_area: {
        player_minimum: "צריך לפחות שני שחקנים במשחק כדי שניתן יהיה להתחיל את המשחק",
      },
      status_indicator: {
        your_turn: "תורך",
        player_playing: "{{player}} משחק...",
        roll_dice: "גלגל את הקובייה",
      },
      players_menu: {
        title: "שחקנים",
      },
      mobile: {
        rotate_to_play: "סובב את המכשיר לרוחב כדי לשחק",
      },
      stageNames: {
        character_select: "בחירת דמות",
        card_draw: "משיכת קלף",
        ability_selection: "בחירת יכולת",
        ability_opponent_selection: "בחירת יעד ליכולת",
        opponent_selection: "בחירת יריב",
        battle_dice_roll: "גלגול קוביות",
        battle_end: "תוצאות קרב",
      },
      stageInstructions: {
        character_select: "בחר דמות",
        card_draw: "משוך קלף מהחפיסה",
        ability_selection: "בחר יכולת",
        ability_opponent_selection: "בחר יריב ודמות להחלת היכולת",
        opponent_selection: "בחר את יריבך",
        battle_dice_roll: "גלגל את הקוביות",
        battle_end: "תוצאות הקרב",
      },
      characterNames: {
        knight: "אביר",
        archer: "קשת",
        mage: "קוסם",
      },
      abilities: {
        battle_howl: {
          name: "שאגת קרב",
          description: "+2 להתקפה",
        },
        bouncing_arrow: {
          name: "חץ מקפץ",
          description: "מאפשר לגלגל את הקובייה מחדש",
        },
        freeze: {
          name: "הקפאה",
          description: "מונע מדמות לבחירתך להשתתף בסיבוב הבא",
        },
      },
      cards: {
        metal_armor: {
          name: "שריון מתכת",
          description: "+2 להגנה - מפחית נזק נכנס",
        },
        sacred_sord: {
          name: "חרב קדושה",
          description: '+3 להתקפה - לא ניתן לשימוש ע"י קשת',
        },
        golden_apple: {
          name: "תפוח זהב",
          description: "+1 לבריאות - לא מעל המקסימום",
        },
        magic_ball: {
          name: "כדור קסם",
          description: "מעלה דרגה ומחזיר בריאות למקסימום",
        },
      },
      card_draw: {
        deck: "חפיסה",
        select: "בחר",
        drawing: "מושך קלף...",
      },
      character_card: {
        level: "דרגה",
      },
      character_select: {
        submit: "בחר",
        select_character: "בחר דמות בבקשה",
        skip_turn: "דלג על תור",
      },
      ability_selection: {
        submit: "בחר",
        select_ability: "בחר יכולת בבקשה",
      },
      ability_opponent_selection: {
        submit: "בחר",
        select_opponent: "בחר יריב ודמות בבקשה",
      },
      opponent_selection: {
        select_opponent: "בחר יריב ודמות בבקשה",
      },
      battle: {
        roll_the_dice: "גלגל את הקובייה",
        roll_the_dice_mult: "גלגל את הקוביות",
        total: 'סה"כ',
        winner: "מנצח",
        continue: "המשך",
        reroll: "גלגל מחדש",
      },
      // cards: {
      //   talisman: "קמע",
      //   talisman_desc: "משמיד (ולא רק מוריד דרגה) את כל מי שהדמות העונדת אותו מביסה (מורידה לה את כל האסימונים).",
      // },
      errors: {
        game_not_found: "המשחק '{{gamename}}' לא נמצא. בדוק את שם המשחק ונסה שוב.",
        connection_failed: "נכשל בהתחברות למשחק. נסה שוב מאוחר יותר.",
      },
      notify: {
        connected: "התחברת למשחק",
        disconnected: "התתקת מהמשחק",
        leaving_game: "עוזב משחק",
      },
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "he", // Hebrew only for now
  fallbackLng: "he",
  interpolation: {
    escapeValue: false, // React already escapes values
  },
});

export default i18n;
