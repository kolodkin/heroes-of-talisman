import React, { useState, useEffect } from 'react';
import './HomePage.css';

const HomePage = () => {
  const [games, setGames] = useState([]);
  const [name, setName] = useState('');
  const [newGameName, setNewGameName] = useState('');

  useEffect(() => {
    // Fetch active games from the server
    // fetch('/api/games')
    //   .then(response => response.json())
    //   .then(data => setGames(data))
    //   .catch(error => console.error('Error fetching games:', error));
    setGames([
      { id: 1, name: 'Game 1' },
      { id: 2, name: 'Game 2' },
      { id: 3, name: 'Game 3' },    
    ])
  }, []);

  const handleNameChange = (event) => {
    setName(event.target.value);
  };

  const handleNewGameNameChange = (event) => {
    setNewGameName(event.target.value);
  };

  const addNewGame = () => {
    const newGame = { id: games.length + 1, name: newGameName };
    setGames([...games, newGame]);
    setNewGameName('');
  };

  const joinGame = (gameId) => {
    console.log(`Joining game with ID: ${gameId}`);
    // Implement the logic to join the game
  };

  return (
    <div className="homepage">
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
        <button onClick={addNewGame}>+</button>
      </div>
      <h2>Join A Game:</h2>
      <ul>
        {games.map(game => (
          <li key={game.id}>
            <button onClick={() => joinGame(game.id)}>{game.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HomePage;