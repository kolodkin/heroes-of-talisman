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
  const [searchResults, setSearchResults] = useState([]);
  const [searchOffset, setSearchOffset] = useState(0);
  const [hasMoreResults, setHasMoreResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchTimeoutRef = useRef(null);
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const getGames = async () => {
    const response = await fetch("/api/games/");
    const games = await response.json();
    console.log("Games:", games);
    setGames(games);
  };

  const addNewGame = async (newGameName) => {
    const response = await fetch("/api/games/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: newGameName }),
    });
    const msg = await response.json();
    console.log("New game:", msg);
    if (!response.ok) {
      toast.error(msg.detail);
    }
    await getGames();
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

    await getGames();
  };

  const searchGames = useCallback(async (query, offset = 0, append = false) => {
    if (!query.trim()) {
      setSearchResults([]);
      setHasMoreResults(false);
      setShowDropdown(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(
        `/api/games/search?q=${encodeURIComponent(query)}&offset=${offset}&limit=${SEARCH_LIMIT}`,
      );
      const data = await response.json();

      if (append) {
        setSearchResults((prev) => [...prev, ...data.games]);
      } else {
        setSearchResults(data.games);
      }
      setHasMoreResults(data.has_more);
      setSearchOffset(offset);
      setShowDropdown(true);
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

  useEffect(() => {
    getGames();
  }, []);

  // Handle click outside dropdown to close it
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
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

  const handleSearchResultClick = (gameName) => {
    setNewGameName(gameName);
    setSearchResults([]);
    setShowDropdown(false);
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
            <div className={styles["search-wrapper"]}>
              <input
                ref={inputRef}
                className={styles.input}
                type="text"
                value={newGameName}
                onChange={handleNewGameNameChange}
                onFocus={() => newGameName.trim() && searchResults.length > 0 && setShowDropdown(true)}
                data-testid="game-name-input"
              />
              {showDropdown && (
                <div ref={dropdownRef} className={styles["search-dropdown"]} data-testid="search-dropdown">
                  {isSearching && searchResults.length === 0 ? (
                    <div className={styles["search-loading"]}>Searching...</div>
                  ) : searchResults.length > 0 ? (
                    <>
                      {searchResults.map((game, index) => (
                        <div
                          key={index}
                          className={styles["search-result"]}
                          onClick={() => handleSearchResultClick(game)}
                          data-testid="search-result"
                        >
                          {game}
                        </div>
                      ))}
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
                  ) : (
                    <div className={styles["search-no-results"]}>No games found</div>
                  )}
                </div>
              )}
            </div>
          </label>
          <button className={styles.button} onClick={handleNewGame}>
            +
          </button>
        </div>
        <h2 data-section="join-game">Join A Game:</h2>
        <ul>
          {games.map((game, index) => (
            <li key={index} className={styles["game-list-item"]}>
              <button className={styles.button} onClick={() => joinGame(game)}>
                {game}
              </button>
              <button className={styles["game-list-delete"]} onClick={() => handleDeleteGame(game)}>
                🗑️
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default HomePage;
