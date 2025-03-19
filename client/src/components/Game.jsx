import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import './Game.css';

const charachterNames = {
    'knight': 'אביר',
    'archer': 'קשת',
    'mage': 'קוסם',
}

const charachtersInfo = {
    'knight': {
        'health': 2,
        'max_health': 2,
        'level': 1,
        'skills': {},
        'dice': 2,
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

const defaultGame = {
    'players': {
        'אדם': {
            'cards': [],
            'characters': {
                'knight': {
                },
                'archer': {
                },
                'mage': {
                },
            }
        },
        'מרק': {
            'cards': [],
            'characters': {
                'knight': {
                },
                'archer': {
                },
                'mage': {
                },
            }
        }
    },
}

const DiceIcon = ({ size, color, fill }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} xmlns="http://www.w3.org/2000/svg">
        <rect width="24" height="24" rx="4" />
        <circle cx="8" cy="8" r="1.5" fill={color} />
        <circle cx="16" cy="8" r="1.5" fill={color} />
        <circle cx="8" cy="16" r="1.5" fill={color} />
        <circle cx="16" cy="16" r="1.5" fill={color} />
    </svg>
);

const CharachterCard = ({ name, character }) => {
    const nameStr = charachterNames[name];
    const info = charachtersInfo[name];

    return (
        <div className='charachter'>
            <img src={`/images/${name}.png`} alt={name} style={{ width: '100px', height: '100px' }} />
            <p>{nameStr}</p>
            <div className='flex space-x-1'>
                {[...Array(info.dice).keys()].map((i) => (<DiceIcon color="white" fill="black" size={"20px"} key={i} />))}
            </div>
        </div>

    )
}

const Board = ({ username, userData }) => {
    const { characters } = userData;
    return (
        <div className='player-board'>
            <div className='player-info'>
                <h2>{username}</h2>
            </div>
            <div className="characters">
                {Object.entries(characters).map(([name, character]) => (
                    <CharachterCard key={name} name={name} character={character} />
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