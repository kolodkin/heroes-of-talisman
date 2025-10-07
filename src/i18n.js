import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  he: {
    translation: {
      direction: "rtl",
      game_name: "Heroes of Talisman",
      disconnected: "התנתקת מהמשחק",
      nav: {
        playing: "משחק",
      },
      stageNames: {
        character_select: "בחירת דמות",
        opponent_selection: "בחירת יריב",
        card_draw: "שליפת קלף",
        use_skill: "שימוש ביכולת",
        battle: "קרב",
      },
      stageInstructions: {
        character_select: "בחר דמות",
        opponent_selection: "בחר את יריבך",
        battle: "בחר דמות יריב לתקוף או דלג",
      },
      characterNames: {
        knight: "אביר",
        archer: "קשת",
        mage: "קוסם",
      },
      character_card: {
        level: "דרגה",
      },
      character_select: {
        submit: "בחר",
        select_character: "בחר דמות בבקשה",
      },
      opponent_selection: {
        select_opponent: "בחר יריב ודמות בבקשה",
      },
      battle: {
        roll: "גלגל את הקובייה",
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
