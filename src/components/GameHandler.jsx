import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { notify, enotify } from "../utils/notify";
import AppWebSocket from "../utils/ws";
import styles from "./GameHandler.module.css";

import lang from "./he";
import { toast } from "react-toastify";

const MAX_RECONNECT_RETRIES = 20;
const RECONNECT_TIMEOUT_MS = 500;

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
    enotify("errors.connection_failed");
    return;
  };

  const onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("onmessage", data);
    // handle error message
    if (data.error) {
      // special casses
      if (data.error === "Game not found") {
        enotify("errors.game_not_found", gamename);
        navigate("/");
        socketRef.current?.close();
        return;
      }
      console.error(data.class || "error", data.error);
      if (data.class == "ReportedException") {
        toast.error(data.error);
      } else {
        toast.error("Server Error. If this error persists, please contact the administrator.");
      }
    } else if (data.event === "game_update") {
      setGame(data.game);
    }
  };

  const onopen = () => {
    notify("notify.connected");
    setConnected(true);
    sendAction("connect");
  };

  const onclose = (closing, retries) => {
    console.log(`WebSocket closed, closing: ${closing}, retries: ${retries}`);
    if (closing || retries != 0) {
      return;
    }

    setConnected(false);
    enotify("disconnected");
  };

  const onerror = (error) => {
    console.error("WebSocket error:", error);
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
    socketRef.current = AppWebSocket({
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
      console.log("Unmounting Game component");
      socketRef.current?.close();
    };
  }, [gamename, username]);

  const sendAction = (action, data = {}) => {
    const socket = socketRef.current;
    if (socket) {
      socket.sendAction(username, action, data);
    } else {
      console.log("socket not connected");
    }
  };

  const handleLeave = () => {
    notify("notify.leaving_game");
    sendAction("leave");
    socketRef.current?.close();
    navigate("/");
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
    <div className={styles["game-handler"]} style={{ direction: lang.direction }}>
      <div>Hi</div>
      {disconnectedOverlay}
    </div>
  );
};

export default Game;
