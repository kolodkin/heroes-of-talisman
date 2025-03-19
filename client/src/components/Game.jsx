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
    'knight-1': {
        'health': 2,
        'max_health': 2,
        'skills': {},
        'dice': 2,
        'attack': 1,
    },
    'archer-1': {
        'health': 3,
        'max_health': 3,
        'skills': {},
        'dice': 1,
    },
    'mage-1': {
        'health': 2,
        'max_health': 2,
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
                    'health': 2,
                    'level': 1,
                },
                'archer': {
                    'health': 2,
                    'level': 1,
                },
                'mage': {
                    'health': 1,
                    'level': 1,
                },
            }
        },
        'מרק': {
            'cards': [],
            'characters': {
                'knight': {
                    'health': 2,
                    'level': 1,
                },
                'archer': {
                    'health': 3,
                    'level': 1,
                },
                'mage': {
                    'health': 2,
                    'level': 1,
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

const HeartIcon = ({ size, color }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color} xmlns="http://www.w3.org/2000/svg">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
    </svg>
);

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : '');

const CharachterCard = ({ name, character }) => {
    const nameStr = charachterNames[name];
    const info = charachtersInfo[`${name}-${character.level}`];

    return (
        <div className='charachter'>
            <img src={`/images/${name}.png`} alt={name} style={{ width: '100px', height: '100px' }} />
            <p className="align-text-center w-full">{nameStr} דרגה {character.level}</p>
            <div className='flex space-x-1'>
                {[...Array(info.dice).keys()].map((i) => (<DiceIcon color="white" fill="black" size={"20px"} key={i} />))}
                <span>{signStr(info.attack)}</span>
            </div>
            <div className='flex items-center'>
                {/* {[...Array(character.health).keys()].map((i) => (<HeartIcon color="red" size={"20px"} key={i} />))} */}
                <HeartIcon color="red" size={"20px"} />
                <span>[{character.health}/{info.max_health}]</span>
            </div>
        </div>
    )
}

const Board = ({ username, userData }) => {
    const { characters } = userData;
    return (
        <div className='player-board'>
            <div className='player-info'>
                <p className='text-2xl'>{username}</p>
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