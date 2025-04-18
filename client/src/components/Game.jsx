import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { notify, enotify } from '../utils/notify';
import ReconnectWebSocket from '../utils/reconnect_ws';
import styles from './Game.module.css';
import classNames from 'classnames';

import { DiceIcon, HeartIcon } from './Icons';
import CharacterSelect from './CharachterSelect';
import DrawCard from './DrawCard';
import lang from './he'
import { toast } from 'react-toastify';


const MAX_RECONNECT_RETRIES = 20;
const RECONNECT_TIMEOUT_MS = 500;


const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : '');

const processGame = (game, username) => {
    game.active = game.playing === username;
    return game;
}

const Board = ({ username, playerData, playing, selected_character }) => {
    const { characters } = playerData;

    const disconnected = playerData.status === 'disconnected'
        ? <div className={classNames(styles['disconnected-card'], 'flex justify-center items-center absolute w-full h-full')}> {lang.player_card.disconnected}</ div>
        : null;
    return (
        <div className={classNames('relative', styles['player-board'], { [styles.playing]: playing })}>
            {disconnected}
            <div className={styles['player-info']}>
                <p className='text-2xl'>{username}</p>
                <p>({playing ? lang.playing : lang.waiting_his_turn})</p>
            </div>
            <div className={styles.characters}>
                {Object.entries(characters).map(([name, character]) => (
                    <CharachterCard key={name} name={name} character={character} selected={character == selected_character} />
                ))}
            </div>
        </div>
    );
};

const CharachterCard = ({ name, character, selected }) => {
    const nameStr = lang.charachterNames[name];

    return (
        <div className={classNames(styles.character, { [styles.selected]: selected })}>
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
        case 'card_draw':
            content = <DrawCard sendAction={sendAction} card={game.stage_meta.card} active={game.active} />
            break
    }


    return (
        <div className={classNames(styles['action-board'], 'relative', 'p-4')}>
            <div className='absolute top-2 end-2 flex space-x-2'>
                <p className='text-xl'>{username} @ {gamename}</p>
                <div className={styles['disconnect-button']} onClick={handleLeave} title="צא מהמשחק"><span>X</span></div>
            </div>
            <div className={styles.stage}>
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
    const [connected, setConnected] = useState(false);
    const { gamename, username } = navparams;
    const [game, setGame] = useState(null);
    const socketRef = useRef(null);
    const isFirstRender = useRef(true);


    /* socket callbacks */
    const onMaxRetries = () => {
        enotify('errors.connection_failed');
        return
    }

    const onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('onmessage', data);
        // handle error message
        if (data.error) {
            // special casses
            if (data.error === 'Game not found') {
                enotify('errors.game_not_found', gamename);
                navigate('/');
                socketRef.current?.close();
                return;
            }
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
        notify('notify.connected');
        setConnected(true);
        sendAction('connect');
    };

    const onclose = (closing, retries) => {
        console.log(`WebSocket closed, closing: ${closing}, retries: ${retries}`);
        if (closing || retries != 0) {
            return;
        }

        setConnected(false);
        enotify('disconnected');
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
        notify('notify.leaving_game');
        sendAction('leave');
        socketRef.current?.close();
        navigate('/');
    };


    if (!game) {
        return <div>Loading...</div>;
    }

    const disconnectedOverlay = !connected ? (
        <div className={styles.disconnected}>
            <p>{lang.disconnected}</p>
        </div>
    ) : null;

    return (
        <div className={styles.game}>
            <div className={classNames(styles['game-content'], { ['active-player']: game.active })}>
                <ActionBoard username={username} gamename={gamename} game={game} sendAction={sendAction} handleLeave={handleLeave} />
                <div className={styles.players}>
                    {Object.entries(game.players).map(([username, playerData]) => (
                        <Board key={username} username={username} playerData={playerData}
                            playing={game.playing === username}
                            selected_character={game.playing === username ? game.selected_character : null} />
                    ))}
                </div>
            </div>
            {disconnectedOverlay}
        </div >
    );
};

export default Game;