import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import className from "classnames";
import styles from "./GamePlay.module.css";
import commonStyles from "./Common.module.css";
import CharacterCard from "./CharacterCard";
import StageCharacterSelect from "./StageCharacterSelect";
import StageCardDraw from "./StageCardDraw";
import StageAbilitySelection from "./StageAbilitySelection";
import StageAbilityOpponentSelection from "./StageAbilityOpponentSelection";
import StageAbilityItemSelection from "./StageAbilityItemSelection";
import StageOpponentSelection from "./StageOpponentSelection";
import StageBattle from "./StageBattle";
import Player from "./Player";
import { StatusIndicator } from "./StatusIndicator";
import { FadeProvider } from "./Fade";
import {
  CHARACTER_SELECT,
  CARD_DRAW,
  ABILITY_SELECTION,
  ABILITY_OPPONENT_SELECTION,
  ABILITY_ITEM_SELECTION,
  OPPONENT_SELECTION,
  BATTLE_DICE_ROLL,
  BATTLE_END,
} from "../constants/stages";

const PlayersCards = ({ player }) => {
  return (
    <div className={commonStyles.cardsContainer} data-player-cards>
      {player.characters &&
        Object.entries(player.characters).map(([charName, character]) => (
          <CharacterCard key={charName} name={charName} character={character} />
        ))}
    </div>
  );
};

const PlayersMinified = ({ player }) => {
  const { t } = useTranslation();
  return (
    <div className={styles["player-minimized"]}>
      {player.characters &&
        Object.entries(player.characters).map(([charName, character]) => (
          <div key={charName} className={styles["character-minimized"]} data-character={charName}>
            <span className={styles["character-name"]}>{t(`characterNames.${charName}`)}</span>
            <span className={styles["character-level"]} data-level={character.level}>
              {t("character_card.level")} {character.level}
            </span>
          </div>
        ))}
    </div>
  );
};

const MOBILE_QUERY = "(max-height: 500px) and (orientation: landscape)";

const GamePlay = ({ username, gamePlay, sendAction }) => {
  const { t } = useTranslation();
  const isRtl = t("direction") === "rtl";

  const [displayedGamePlay, setDisplayedGamePlay] = useState(gamePlay);
  const [leaving, setLeaving] = useState(false);
  const prevStageRef = useRef(gamePlay.stage);

  useEffect(() => {
    if (gamePlay.stage !== prevStageRef.current) {
      prevStageRef.current = gamePlay.stage;
      setLeaving(true);
      const timer = setTimeout(() => {
        setDisplayedGamePlay(gamePlay);
        setLeaving(false);
      }, 500);
      return () => clearTimeout(timer);
    } else {
      setDisplayedGamePlay(gamePlay);
    }
  }, [gamePlay]);

  // Three states: "collapsed" | "minimized" | "expanded"
  const [playersMenuState, setPlayersMenuState] = useState(() => {
    return window.matchMedia(MOBILE_QUERY).matches ? "collapsed" : "minimized";
  });

  // Listen for viewport changes to update default state
  useEffect(() => {
    const mql = window.matchMedia(MOBILE_QUERY);
    const handler = (e) => {
      setPlayersMenuState(e.matches ? "collapsed" : "minimized");
    };
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  if (!gamePlay || !gamePlay.players) {
    return null;
  }

  // Convert players object to array
  const playersArray = Object.values(gamePlay.players);

  if (playersArray.length === 0) {
    return null;
  }

  // Check total player count (regardless of connection status)
  const hasMinimumPlayers = playersArray.length >= 2;

  const collapseMenu = () => setPlayersMenuState("collapsed");
  const toggleExpandMinimize = () => {
    setPlayersMenuState((prev) => (prev === "expanded" ? "minimized" : "expanded"));
  };
  const expandFromCollapsed = () => setPlayersMenuState("minimized");

  // Determine status indicator for SharedArea overlay
  const getStatusIndicator = () => {
    const isActivePlayer = gamePlay?.active?.player === username;
    const isOpponentRoll =
      gamePlay?.stage === BATTLE_DICE_ROLL && gamePlay?.opponent?.player === username && !gamePlay?.opponent?.dice_roll;

    if (isActivePlayer) {
      return { status: "your_turn" };
    } else if (isOpponentRoll) {
      return { status: "roll_dice" };
    } else {
      return {
        status: "opponent_playing",
        playerName: gamePlay?.active?.player,
      };
    }
  };

  const statusIndicator = getStatusIndicator();

  return (
    <div className={styles["game-play"]} data-game-stage={gamePlay.stage} data-players-menu-state={playersMenuState}>
      <div className={styles["portrait-overlay"]}>
        <div className={styles["portrait-overlay-content"]}>
          <span className={styles["rotate-icon"]}>📱</span>
          <span>{t("mobile.rotate_to_play")}</span>
        </div>
      </div>
      {playersMenuState !== "collapsed" && (
        <div className={styles["players-container"]}>
          <div className={styles["players-header"]}>
            <span className={styles["players-title"]}>{t("players_menu.title")}</span>
            <div className={styles["header-buttons"]}>
              <button
                className={styles["toggle-button"]}
                onClick={toggleExpandMinimize}
                aria-label={playersMenuState === "minimized" ? "Expand all players" : "Minimize all players"}
              >
                {playersMenuState === "minimized" ? "+" : "−"}
              </button>
              <button
                className={styles["toggle-button"]}
                onClick={collapseMenu}
                aria-label="Collapse players menu"
                data-collapse-button
              >
                {isRtl ? "<" : ">"}
              </button>
            </div>
          </div>
          {playersArray.map((player) => {
            const playerDom =
              playersMenuState === "minimized" ? <PlayersMinified player={player} /> : <PlayersCards player={player} />;

            return (
              <Player key={player.name} player={player} className={styles.player} showDisconnected={true}>
                <div className={styles["player-name"]}>{player.name}</div>
                {playerDom}
              </Player>
            );
          })}
        </div>
      )}

      <div
        className={className(styles["shared-area"], {
          [styles["shared-area-disabled"]]: gamePlay.active?.player !== username,
          [styles["shared-area-battle"]]: gamePlay.stage === BATTLE_DICE_ROLL || gamePlay.stage === BATTLE_END,
          [styles["shared-area-actionable"]]:
            statusIndicator.status === "your_turn" || statusIndicator.status === "roll_dice",
        })}
        data-shared-area-active={gamePlay.active?.player === username}
      >
        {!hasMinimumPlayers && (
          <div className={commonStyles["gray-overlay"]} data-minimum-player-overlay>
            <div className={`${commonStyles["gray-overlay-text"]} ${styles["minimum-player-text"]}`}>
              {t("shared_area.player_minimum")}
            </div>
          </div>
        )}
        <StatusIndicator status={statusIndicator.status} playerName={statusIndicator.playerName} />
        {playersMenuState === "collapsed" && (
          <button
            className={styles["expand-overlay-button"]}
            onClick={expandFromCollapsed}
            aria-label="Expand players menu"
            data-expand-button
          >
            {isRtl ? ">" : "<"}
          </button>
        )}
        <FadeProvider value={leaving}>
          <div className={styles["shared-area-content"]}>
            <h2 className={styles["stage-title"]}>{t(`stageInstructions.${displayedGamePlay.stage}`)}</h2>
            {(() => {
              const activePlayer = displayedGamePlay.players[displayedGamePlay.active?.player];
              const isActivePlayer = displayedGamePlay.active?.player === username;

              switch (displayedGamePlay.stage) {
                case CHARACTER_SELECT:
                  return (
                    <StageCharacterSelect
                      characters={activePlayer?.characters || {}}
                      sendAction={sendAction}
                      active={isActivePlayer}
                      selectedCharacter={displayedGamePlay.stage_meta?.selected}
                    />
                  );
                case CARD_DRAW:
                  return (
                    <StageCardDraw
                      drawnCard={displayedGamePlay.stage_meta?.drawn_card}
                      sendAction={sendAction}
                      active={isActivePlayer}
                    />
                  );
                case ABILITY_SELECTION:
                  const selectedCharacter = activePlayer?.characters?.[displayedGamePlay.active?.character];
                  return (
                    <StageAbilitySelection
                      abilities={selectedCharacter?.abilities || []}
                      sendAction={sendAction}
                      active={isActivePlayer}
                      selectedAbility={displayedGamePlay.stage_meta?.selected}
                    />
                  );
                case ABILITY_OPPONENT_SELECTION:
                  return (
                    <StageAbilityOpponentSelection
                      players={displayedGamePlay.players}
                      activePlayer={displayedGamePlay.active?.player}
                      sendAction={sendAction}
                      active={isActivePlayer}
                      selectedOpponent={displayedGamePlay.stage_meta}
                    />
                  );
                case ABILITY_ITEM_SELECTION:
                  return (
                    <StageAbilityItemSelection
                      stageMeta={displayedGamePlay.stage_meta}
                      players={displayedGamePlay.players}
                      sendAction={sendAction}
                      active={isActivePlayer}
                    />
                  );
                case OPPONENT_SELECTION:
                  return (
                    <StageOpponentSelection
                      players={displayedGamePlay.players}
                      activePlayer={displayedGamePlay.active?.player}
                      sendAction={sendAction}
                      active={isActivePlayer}
                      selectedOpponent={displayedGamePlay.stage_meta}
                    />
                  );
                case BATTLE_DICE_ROLL:
                case BATTLE_END:
                  return (
                    <StageBattle
                      gamePlay={displayedGamePlay}
                      sendAction={sendAction}
                      active={isActivePlayer}
                      currentUser={username}
                    />
                  );
                default:
                  return <div>Stage: {displayedGamePlay.stage}</div>;
              }
            })()}
          </div>
        </FadeProvider>
      </div>
    </div>
  );
};

export default GamePlay;
