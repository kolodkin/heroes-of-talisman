import React, { useState, useEffect } from 'react';
import './HomePage.css';

const HomePage = () => {
    const [games, setGames] = useState([]);
    const [name, setName] = useState('');
    const [newGameName, setNewGameName] = useState('');

    const getGames = async () => {
        const response = await fetch('/api/games');
        const games = await response.json();
        console.log('Games:', games);
        setGames(games);
    }

    const addNewGame = async (newGameName) => {
        const response = await fetch('/api/games', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newGameName }),
        });
        const msg = await response.json();
        console.log('New game:', msg);
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
        await getGames();
    }

    useEffect(() => {
        getGames();
    }, []);

    const handleNameChange = (event) => {
        setName(event.target.value);
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

    const joinGame = (gameId) => {
        console.log(`Joining game with ID: ${gameId}`);
        // Implement the logic to join the game
    };

    return (
        <div className="homepage">
            <div className="homepage-container">
                <h1>Welcome to Heroes of Talisman</h1>
                <div className="input-container">
                    <label>
                        Enter your name:
                        <input type="text" value={name} onChange={handleNameChange} />
                    </label>
                </div>
                <div className="input-container">
                    <label>
                        Add New Game:
                        <input type="text" value={newGameName} onChange={handleNewGameNameChange} />
                    </label>
                    <button onClick={handleNewGame}>+</button>
                </div>
                <h2>Join A Game:</h2>
                <ul>
                    {games.map((game, index) => (
                        <li key={index} className="game-list-item">
                            <button onClick={() => joinGame(index + 1)}>{game}</button>
                            <button className="game-list-delete" onClick={() => handleDeleteGame(game)}>🗑️</button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default HomePage;