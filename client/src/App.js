import React, { useState, useEffect } from 'react';

const App = () => {
  const [name, setName] = useState('');
  const [gameId, setGameId] = useState('');
  const [gameState, setGameState] = useState(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    if (ws) {
      ws.onmessage = (event) => {
        setGameState(JSON.parse(event.data));
      };
    }
  }, [ws]);

  const handleConnect = () => {
    const socket = new WebSocket(`ws://localhost:8000/ws/${gameId}`);
    setWs(socket);
  };

  const handleCreateGame = () => {
    const newGameId = Math.random().toString(36).substring(2, 15);
    setGameId(newGameId);
    handleConnect();
  };

  const handleJoinGame = () => {
    handleConnect();
  };

  return (
    <div>
      {!gameState ? (
        <div>
          <h1>Welcome to the Board Game</h1>
          <input
            type="text"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button onClick={handleCreateGame}>Create Game</button>
          <input
            type="text"
            placeholder="Enter game ID"
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
          />
          <button onClick={handleJoinGame}>Join Game</button>
        </div>
      ) : (
        <div>
          <h1>Game Board</h1>
          <pre>{JSON.stringify(gameState, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
