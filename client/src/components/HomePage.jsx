import React, { useState, useEffect } from 'react';
import './HomePage.css';

const HomePage = () => {
  const [games, setGames] = useState([]);
  const [name, setName] = useState('');

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

  return (
    <div className="homepage">
      <h1>Welcome to Heroes of Talisman</h1>
      <div className="input-container">
        <label>
          Enter your name:
          <input type="text" value={name} onChange={handleNameChange} />
        </label>
      </div>
      <h2>Active Games</h2>
      <ul>
        {games.map(game => (
          <li key={game.id}>{game.name}</li>
        ))}
      </ul>
    </div>
  );
};

export default HomePage;