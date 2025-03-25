import React, { useState, useEffect } from 'react';
import styles from './HomePage.module.css'
import classNames from 'classnames';

import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
    const [games, setGames] = useState([]);
    const [username, setUserName] = useState(localStorage.getItem('username') || '');
    const [newGameName, setNewGameName] = useState('');
    const navigate = useNavigate();

    const getGames = async () => {
        const response = await fetch('/api/games/');
        const games = await response.json();
        console.log('Games:', games);
        setGames(games);
    }

    const addNewGame = async (newGameName) => {
        const response = await fetch('/api/games/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newGameName }),
        });
        const msg = await response.json();
        console.log('New game:', msg);
        if (!response.ok) {
            toast.error(msg.detail);
        }
        await getGames();
    }

    const deleteGame = async (gameName) => {
        const response = await fetch('/api/games/' + gameName, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const msg = await response.json();
        console.log('Delete game:', msg);
        if (!response.ok) {
            toast.error(msg.message);
        }

        await getGames();
    }

    useEffect(() => {
        getGames();
    }, []);

    const handleNameChange = (event) => {
        const newUsername = event.target.value;
        setUserName(newUsername);
        localStorage.setItem('username', newUsername);
    };

    const handleNewGameNameChange = (event) => {
        setNewGameName(event.target.value);
    };

    const handleNewGame = (event) => {
        addNewGame(newGameName);
    }

    const handleDeleteGame = (gameName) => {
        deleteGame(gameName);
    }

    const joinGame = (gameName) => {
        navigate(`/games/${gameName}/${username}`);
    };

    return (
        <div className={styles.homepage}>
            <div className={styles['homepage-container']}>
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
                        <input className={styles.input} type="text" value={newGameName} onChange={handleNewGameNameChange} />
                    </label>
                    <button className={styles.button} onClick={handleNewGame}>+</button>
                </div>
                <h2>Join A Game:</h2>
                <ul>
                    {games.map((game, index) => (
                        <li key={index} className={styles["game-list-item"]}>
                            <button className={styles.button} onClick={() => joinGame(game)}>{game}</button>
                            <button className={styles["game-list-delete"]} onClick={() => handleDeleteGame(game)}>🗑️</button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default HomePage;