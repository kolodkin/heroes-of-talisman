import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import './Game.css';

const charachterName = {
    'knight': 'אביר',
    'archer': 'קשת',
    'mage': 'קוסם',
}

const defaultGame = {
    'players': {
        'אדם': {
            'cards': [],
            'characters': {
                'knight': {
                    'health': 2,
                    'max_health': 2,
                    'level': 1,
                    'skills': {},
                    'dice': 1,
                },

                'archer': {
                    'health': 3,
                    'max_health': 3,
                    'level': 1,
                    'skills': {},
                    'dice': 1,
                },
                'mage': {
                    'health': 2,
                    'max_health': 2,
                    'level': 1,
                    'skills': {},
                    'dice': 1,
                },
            }
        },
        'מרק': {
            'cards': [],
            'characters': {
                'knight': {
                    'health': 2,
                    'max_health': 2,
                    'level': 1,
                    'skills': {},
                    'dice': 1,
                },

                'archer': {
                    'health': 3,
                    'max_health': 3,
                    'level': 1,
                    'skills': {},
                    'dice': 1,
                },
                'mage': {
                    'health': 2,
                    'max_health': 2,
                    'level': 1,
                    'skills': {},
                    'dice': 1,
                },
            }
        }
    },
}

const Board = ({ username, userData }) => {
    const { characters } = userData;
    return (
        <div className='player-board'>
            <div className='player-info'>
                <h2>{username}</h2>
            </div>
            <div className="characters">
                {Object.keys(characters).map((character, index) => (
                    <div className='charachter' key={index}>
                        <img src={`/images/${character}.png`} alt={character} style={{ width: '100px', height: '100px' }} />
                        <p>{charachterName[character]}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};


const Game = () => {
    const navparams = useParams();
    const { gameName, username } = navparams;
    const [game, setGame] = useState(defaultGame);
    const socketRef = useRef(null);
    const isFirstRender = useRef(true);

    useEffect(() => {
        // handle strict mode re-render
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }

        console.log('useEffect called');
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        socketRef.current = new WebSocket(`${protocol}://${window.location.host}/ws/${gameName}/${username}`);
        // socketRef.current = new WebSocket(`/ws`);
        // socketRef.current = new WebSocket(`ws://localhost:8080/ws/${gameName}/${username}`);
        const socket = socketRef.current;

        socket.onmessage = (event) => {
            console.log('message', event.data);
        };

        socket.onopen = () => {
            const msg = 'Connected to the game!';
            console.log(msg);
            toast(msg);
        };

        socket.onclose = () => {
            const msg = 'Disconnected from the game.';
            console.log(msg);
            toast(msg);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            toast('WebSocket error occurred.');
        };

        return () => {
            console.log('Unmounting Game component');
            socketRef.current?.close();
            socketRef.current = null;
        };
    }, [gameName, username]);

    const sendMessage = () => {
        const socket = socketRef.current;
        if (socket && input) {
            socket.send(input);
            setInput('');
        }
    };

    return (
        <div className='game'>
            <div className='action-board'>
                <h1>Game: {gameName}</h1>
            </div>
            <div className="players">
                {Object.entries(game.players).map(([username, userData]) => (
                    <Board key={username} username={username} userData={userData} />
                ))}
            </div>
        </div>
    );
};

export default Game;