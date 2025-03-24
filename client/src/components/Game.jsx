import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import './Game.css';

const lang = {
    playing: 'משחק',
    waiting_his_turn: 'ממתין לתורו',
    stargesNames: {
        'character_select': 'בחירת דמות',
        'card_draw': 'שליפת קלפים',
        'use_skill': 'שימוש בכישור',
        'battle': 'קרב',
    },
    charachterNames: {
        'knight': 'אביר',
        'archer': 'קשת',
        'mage': 'קוסם',
    }
}


const defaultGame = {
    'players': {},
    'playing': null,
    'stage': null,
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


const Board = ({ username, userData, playing }) => {
    const { characters } = userData;

    return (
        <div className={`player-board ${playing ? 'playing' : ''}`}>
            <div className='player-info'>
                <p className='text-2xl'>{username}</p>
                <p>({playing ? lang.playing : lang.waiting_his_turn})</p>
            </div>
            <div className="characters">
                {Object.entries(characters).map(([name, character]) => (
                    <CharachterCard key={name} name={name} character={character} />
                ))}
            </div>
        </div>
    );
};

const CharachterCard = ({ name, character }) => {
    const nameStr = lang.charachterNames[name];

    return (
        <div className='charachter'>
            <img src={`/images/${name}.png`} alt={name} style={{ width: '100px', height: '100px' }} />
            <p className="align-text-center w-full">{nameStr} דרגה {character.level}</p>
            <div className='flex items-center space-x-1'>
                {[...Array(character.dice).keys()].map((i) => (<DiceIcon color="white" fill="black" size={"20px"} key={i} />))}
                <span>{signStr(character.attack)}</span>
            </div>
            <div className='flex items-center'>
                {/* {[...Array(character.health).keys()].map((i) => (<HeartIcon color="red" size={"20px"} key={i} />))} */}
                <HeartIcon color="red" size={"20px"} />
                <span>[{character.health}/{character.max_health}]</span>
            </div>
        </div>
    )
}

const CharacterSelect = ({ characters, handleSelect }) => {
    return (
        <div className='character-select'>
        </div>
    )
}

const ActionBoard = ({ username, gamename, game, handleLeave }) => {
    const { stage } = game;
    const stageName = lang.stargesNames[stage];

    return (
        <div className='action-board relative p-4'>
            <div className='absolute top-2 end-2 flex space-x-2'>
                <p className='text-xl'>{username} @ {gamename}</p>
                <div className='disconnect-button' onClick={handleLeave} title="צא מהמשחק"><span>X</span></div>
            </div>
            <div className='stage'>
                <p className='text-3xl'>{stageName}</p>
            </div>
        </div>
    )
}

const Game = () => {
    const navparams = useParams();
    const navigate = useNavigate();
    const { gameName: gamename, username } = navparams;
    const [game, setGame] = useState(defaultGame);
    const socketRef = useRef(null);
    const isFirstRender = useRef(true);

    const notify = (msg) => {
        console.log(msg);
        toast(msg);
    }

    useEffect(() => {
        // handle strict mode re-render
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }

        // todo: implement reconnect logic
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        socketRef.current = new WebSocket(`${protocol}://${window.location.host}/ws/${gamename}/${username}`);
        const socket = socketRef.current;

        socket.onmessage = (event) => {
            console.log('message', event.data);
            const data = JSON.parse(event.data);
            // handle error message
            if (data.error) {
                console.error(data.error);
                toast.error(data.error);
            }
            else if (data.event === 'game_update') {
                setGame(data.game);
            }
        };

        socket.onopen = () => {
            notify('Connected to the game!');
            sendAction('connect');
        };

        socket.onclose = () => {
            notify('Disconnected from the game.');
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            toast.error('WebSocket error occurred.');
        };

        return () => {
            console.log('Unmounting Game component');
            socketRef.current?.close();
            socketRef.current = null;
        };
    }, [gamename, username]);

    const sendAction = (action, data = {}) => {
        const socket = socketRef.current;
        if (socket) {
            socket.send(JSON.stringify({
                username,
                action,
                ...data
            }));
        }
    };

    const handleLeave = () => {
        // Implement disconnect logic here
        console.log(`${username} disconnected`);
        toast(`${username} leaft game`);
        sendAction('leave');
        navigate('/');
    };

    return (
        <div className='game'>
            <ActionBoard username={username} gamename={gamename} game={game} handleLeave={handleLeave} />
            <div className="players">
                {Object.entries(game.players).map(([username, userData]) => (
                    <Board key={username} username={username} userData={userData} playing={username == game.playing} />
                ))}
            </div>
        </div>
    );
};

export default Game;