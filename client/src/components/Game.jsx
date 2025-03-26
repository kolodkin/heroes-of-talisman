import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { notify, enotify } from '../utils/notify';
import ReconnectWebSocket from '../utils/reconnect_ws';
import './Game.css';

import { DiceIcon, HeartIcon } from './Icons';
import CharacterSelect from './CharachterSelect';
import lang from './he'
import { toast } from 'react-toastify';


const MAX_RECONNECT_RETRIES = 5;
const RECONNECT_TIMEOUT_MS = 300;


const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : '');

const processGame = (game, username) => {
    game.active = game.playing === username;
    return game;
}

const Board = ({ username, userData, playing }) => {
    const { characters } = userData;

    const disconnected = userData.status === 'disconnected'
        ? <div className='flex justify-center items-center disconnected-card absolute w-full h-full'>{lang.player_card.disconnected}</div>
        : null;
    return (
        <div className={`relative player-board ${playing ? 'playing' : ''}`}>
            {disconnected}
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
            <img src={`/images/${name}.png`} alt={name} style={{ minWidth: '100px', width: '100px', height: '100px' }} />
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


const ActionBoard = ({ username, gamename, game, sendAction, handleLeave }) => {
    const { stage } = game;
    const stageName = lang.stageNames[stage];
    const stageTitle = lang.stageTitleNames[stage];


    let content;
    switch (stage) {
        case 'character_select':
            content = <CharacterSelect characters={game.players[username].characters} sendAction={sendAction} active={game.active} />
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
    const navigate = useNavigate();
    const navparams = useParams();
    const { gamename, username } = navparams;
    const [game, setGame] = useState(null);
    const socketRef = useRef(null);
    const isFirstRender = useRef(true);

    /* socket callbacks */
    const onMaxRetries = () => {
        enotify('Failed to connect to the game. Please try again later.');
        return
    }

    const onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('onmessage', data);
        // handle error message
        if (data.error) {
            console.error(data.class || 'error', data.error);
            if (data.class == 'ReportedException') {
                toast.error(data.error);
            }
            else {
                toast.error('Server Error. If this error persists, please contact the administrator.');
            }
        }
        else if (data.event === 'game_update') {
            const game = processGame(data.game, username);
            setGame(game);
        }
    }

    const onopen = () => {
        notify('Connected to the game!');
        sendAction('connect');
    };

    const onclose = (closing) => {
        console.log(`WebSocket closed, closing: ${closing}`);
        if (closing) {
            return;
        }

        if (retries == 0) {
            enotify('Disconnected from the game.');
        }
    };

    const onerror = (error) => {
        console.error('WebSocket error:', error);
        // toast.error('WebSocket error occurred.');
    };

    useEffect(() => {
        // handle strict mode re-render
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }


        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const url = `${protocol}://${window.location.host}/ws/${gamename}/${username}`;
        socketRef.current = ReconnectWebSocket({
            url,
            onopen,
            onerror,
            onclose,
            onmessage,
            interval: RECONNECT_TIMEOUT_MS,
            maxRetries: MAX_RECONNECT_RETRIES,
            onMaxRetries,
        });

        return () => {
            console.log('Unmounting Game component');
            socketRef.current?.close();
        };
    }, [gamename, username]);

    const sendAction = (action, data = {}) => {
        console.log(`send action '${action}'`, data)
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
        notify('Leaving game...');
        sendAction('leave');
        socketRef.current?.close();
        navigate('/');
    };


    if (!game) {
        return <div>Loading...</div>;
    }

    return (
        <div className='game'>
            <ActionBoard username={username} gamename={gamename} game={game} sendAction={sendAction} handleLeave={handleLeave} />
            <div className="players">
                {Object.entries(game.players).map(([username, userData]) => (
                    <Board key={username} username={username} userData={userData} playing={game.playing === username} />
                ))}
            </div>
        </div>
    );
};

export default Game;