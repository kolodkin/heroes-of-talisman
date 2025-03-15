// filepath: /home/mark/workspace/heroes-of-talisman/client/src/components/Game.js
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
    players: {
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
    const { gameName, username } = useParams();
    const [game, setGame] = useState(defaultGame);
    const socketRef = useRef(null);

    useEffect(() => {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        socketRef.current = new WebSocket(`${protocol}://${window.location.host}/ws/${gameName}?username=${username}`);
        const socket = socketRef.current;

        socket.onmessage = (event) => {
            const message = event.data;
            setMessages((prevMessages) => [...prevMessages, message]);
        };

        socket.onopen = () => {
            toast('Connected to the game!');
        };

        socket.onclose = () => {
            toast('Disconnected from the game.');
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