// filepath: /home/mark/workspace/heroes-of-talisman/client/src/components/Game.js
import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Game = () => {
    const { gameName, username } = useParams();

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
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
        <div>
            <h1>Game: {gameName}</h1>
            <div>
                {messages.map((msg, index) => (
                    <div key={index}>{msg}</div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default Game;