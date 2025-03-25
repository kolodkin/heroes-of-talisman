import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { notify, enotify } from '../utils/notify';
import './Game.css';

import { DiceIcon, HeartIcon } from './Icons';
import CharacterSelect from './CharachterSelect';
import lang from './he'


const MAX_RECONNECT_RETRIES = 5;
const RECONNECT_TIMEOUT_MS = 300;


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


const ActionBoard = ({ username, gamename, game, sendAction }) => {
    const navigate = useNavigate();

    const { stage } = game;
    const stageName = lang.stageNames[stage];
    const stageTitle = lang.stageTitleNames[stage];


    const handleLeave = () => {
        console.log(`${username} disconnected`);
        toast(`${username} leaft game`);
        sendAction('leave');
        navigate('/');
    };


    let content;
    switch (stage) {
        case 'character_select':
            content = <CharacterSelect characters={game.players[username].characters} sendAction={sendAction} />
            break
    }


    return (
        <div className='action-board relative p-4'>
            <div className='absolute top-2 end-2 flex space-x-2'>
                <p className='text-xl'>{username} @ {gamename}</p>
                <div className='disconnect-button' onClick={handleLeave} title="צא מהמשחק"><span>X</span></div>
            </div>
            <div className='stage'>
                <p className='text-2xl mb-5'>
                    {game.playing !== username ?
                        `${lang.action_board.wait_your_turn} (${stageName} - ${game.playing})`
                        : stageTitle
                    }
                </p>
                {content}
            </div>
        </div>
    )
}

const Game = () => {
    const navparams = useParams();
    const { gameName: gamename, username } = navparams;
    const [game, setGame] = useState(null);
    const socketRef = useRef(null);
    const isFirstRender = useRef(true);
    const connectTimeout = useRef(null);


    useEffect(() => {
        // handle strict mode re-render
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }

        const connectSocket = (retries = 0) => {
            if (retries >= MAX_RECONNECT_RETRIES) {
                enotify('Failed to connect to the game. Please try again later.');
                return
            }

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
                if (connectTimeout.current) {
                    clearTimeout(connectTimeout.current);
                }

                sendAction('connect');
            };

            socket.onclose = () => {
                if (retries == 0) {
                    enotify('Disconnected from the game.');
                }

                connectTimeout = setTimeout(() => connectSocket(retries + 1), RECONNECT_TIMEOUT_MS); // Attempt to reconnect after 200ms
            };

            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                // toast.error('WebSocket error occurred.');
            };
        };

        connectSocket();

        return () => {
            console.log('Unmounting Game component');
            socketRef.current?.close();
            socketRef.current = null;
            if (connectTimeout.current) {
                clearTimeout(connectTimeout.current);
            }
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


    if (!game) {
        return <div>Loading...</div>;
    }

    return (
        <div className='game'>
            <ActionBoard username={username} gamename={gamename} game={game} sendAction={sendAction} />
            <div className="players">
                {Object.entries(game.players).map(([username, userData]) => (
                    <Board key={username} username={username} userData={userData} playing={username == game.playing} />
                ))}
            </div>
        </div>
    );
};

export default Game;