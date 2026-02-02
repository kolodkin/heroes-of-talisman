import React, { useState, useEffect, useRef, useCallback } from "react";

import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import styles from "./HomePage.module.css";

const SEARCH_LIMIT = 5;
const DEBOUNCE_MS = 300;

const HomePage = () => {
  const { t } = useTranslation();
  const [games, setGames] = useState([]);
  const [username, setUserName] = useState(localStorage.getItem("username") || "");
  const [newGameName, setNewGameName] = useState("");
  const [searchOffset, setSearchOffset] = useState(0);
  const [hasMoreResults, setHasMoreResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef(null);
  const navigate = useNavigate();

  const getGames = async () => {
    const response = await fetch("/api/games/");
    const allGames = await response.json();
    console.log("Games:", allGames);
    setGames(allGames);
    setHasMoreResults(false);
  };

  const searchGames = useCallback(async (query, offset = 0, append = false) => {
    if (!query.trim()) {
      // No search query - show all games
      await getGames();
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(
        `/api/games/search?q=${encodeURIComponent(query)}&offset=${offset}&limit=${SEARCH_LIMIT}`,
      );
      const data = await response.json();

      if (append) {
        setGames((prev) => [...prev, ...data.games]);
      } else {
        setGames(data.games);
      }
      setHasMoreResults(data.has_more);
      setSearchOffset(offset);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const loadMoreResults = () => {
    const nextOffset = searchOffset + SEARCH_LIMIT;
    searchGames(newGameName, nextOffset, true);
  };

  const addNewGame = async (gameName) => {
    const response = await fetch("/api/games/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: gameName }),
    });
    const msg = await response.json();
    console.log("New game:", msg);
    if (!response.ok) {
      toast.error(msg.detail);
    }
    // Refresh games list with current search
    searchGames(newGameName, 0, false);
  };

  const deleteGame = async (gameName) => {
    const response = await fetch("/api/games/" + gameName, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });
    const msg = await response.json();
    console.log("Delete game:", msg);
    if (!response.ok) {
      toast.error(msg.message);
    }
    // Refresh games list with current search
    searchGames(newGameName, 0, false);
  };

  useEffect(() => {
    getGames();
  }, []);

  const handleNameChange = (event) => {
    const newUsername = event.target.value;
    setUserName(newUsername);
    localStorage.setItem("username", newUsername);
  };

  const handleNewGameNameChange = (event) => {
    const value = event.target.value;
    setNewGameName(value);

    // Reset pagination for new query
    setSearchOffset(0);

    // Clear existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Debounced search
    searchTimeoutRef.current = setTimeout(() => {
      searchGames(value, 0, false);
    }, DEBOUNCE_MS);
  };

  const handleNewGame = () => {
    addNewGame(newGameName);
  };

  const handleDeleteGame = (gameName) => {
    deleteGame(gameName);
  };

  const joinGame = (gameName) => {
    const trimmedUsername = username.trim();
    if (!trimmedUsername) {
      toast.error(t("home.notify_empty"));
      return;
    }
    navigate(`/games/${gameName}/${trimmedUsername}`);
  };

  return (
    <div className={styles.homepage}>
      <div className={styles["homepage-container"]}>
        <div className={styles["left-section"]}>
          <h1>Welcome to Heroes of Talisman</h1>
          <div className={styles["input-container"]}>
            <label>
              Enter your name:
              <input className={styles.input} type="text" value={username} onChange={handleNameChange} />
            </label>
          </div>
          <div className={styles["input-container"]}>
            <label>
              Add New Game:
              <input
                className={styles.input}
                type="text"
                value={newGameName}
                onChange={handleNewGameNameChange}
                data-testid="game-name-input"
              />
            </label>
            <button className={styles.button} onClick={handleNewGame}>
              +
            </button>
          </div>
        </div>
        <div className={styles["right-section"]}>
          <h2 data-section="join-game">Join A Game:</h2>
          {isSearching && games.length === 0 ? (
            <div className={styles["search-loading"]}>Searching...</div>
          ) : games.length === 0 && newGameName.trim() ? (
            <div className={styles["search-no-results"]}>No games found</div>
          ) : (
            <>
              <ul>
                {games.map((game, index) => (
                  <li key={index} className={styles["game-list-item"]} data-testid="game-list-item">
                    <button className={styles.button} onClick={() => joinGame(game)}>
                      {game}
                    </button>
                    <button className={styles["game-list-delete"]} onClick={() => handleDeleteGame(game)}>
                      🗑️
                    </button>
                  </li>
                ))}
              </ul>
              {hasMoreResults && (
                <button
                  className={styles["load-more-button"]}
                  onClick={loadMoreResults}
                  disabled={isSearching}
                  data-testid="load-more-button"
                >
                  {isSearching ? "Loading..." : "Load more"}
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
