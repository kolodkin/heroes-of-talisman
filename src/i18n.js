import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  he: {
    translation: {
      direction: "rtl",
      playing: "משחק",
      disconnected: "התנתקת מהמשחק",
      waiting_his_turn: "ממתין לתורו",
      stageNames: {
        character_select: "בחירת דמות",
        card_draw: "שליפת קלף",
        use_skill: "שימוש ביכולת",
        battle: "קרב",
      },
      stageTitleNames: {
        character_select: "בחר דמות",
        card_draw: "שלוף קלף",
        use_skill: "בחר יכולת והשתמש בה או דלג",
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
      player_card: {
        disconnected: "התנתק מהמשחק",
      },
      action_board: {
        wait_your_turn: "המתן לתורך",
      },
      character_select: {
        submit: "שלח",
        select_character: "בחר דמות בבקשה",
      },
      draw_card: {
        draw: "שלוף קלף",
        drawen: "שלפת קלף",
        continue: "המשך",
      },
      cards: {
        talisman: "קמע",
        talisman_desc: "משמיד (ולא רק מוריד דרגה) את כל מי שהדמות העונדת אותו מביסה (מורידה לה את כל האסימונים).",
      },
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
