/**
 * DiceView Component
 *
 * Test component for viewing and testing Dice component.
 * Reads dice value from URL query parameter: /dice?value=3
 */
import React from "react";
import { useSearchParams } from "react-router-dom";
import Dice from "./Dice";
import styles from "./DiceView.module.css";

const DiceView = () => {
  const [searchParams] = useSearchParams();
  const value = parseInt(searchParams.get("value")) || 1;
  const noEffect = searchParams.get("noeffect") === "1";

  const parsedDuration = parseInt(searchParams.get("rollDuration"));
  const parsedInterval = parseInt(searchParams.get("rollInterval"));
  const parsedTilt = parseInt(searchParams.get("tilt"));
  const parsedTiltMargin = parseInt(searchParams.get("tiltMargin"));

  const rollDuration = noEffect ? 0 : isNaN(parsedDuration) ? 1200 : parsedDuration;
  const rollInterval = noEffect ? 0 : isNaN(parsedInterval) ? 50 : parsedInterval;
  const tilt = noEffect ? 0 : isNaN(parsedTilt) ? 5 : parsedTilt;
  const tiltMargin = noEffect ? 0 : isNaN(parsedTiltMargin) ? 5 : parsedTiltMargin;
  const [stopped, setStopped] = React.useState(rollDuration === 0);

  const handleStop = React.useCallback(() => {
    setStopped(true);
  }, []);

  // Reset stopped state when value or rollDuration changes
  React.useEffect(() => {
    setStopped(rollDuration === 0);
  }, [value, rollDuration]);

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Dice View</h1>
      <div className={styles.info}>
        <p>Value: {value}</p>
        <p>Status: {stopped ? "Stopped" : "Rolling..."}</p>
      </div>
      <div className={styles.diceContainer} data-dice-stopped={stopped}>
        <Dice
          value={value}
          rollDuration={rollDuration}
          rollInterval={rollInterval}
          tilt={tilt}
          tiltMargin={tiltMargin}
          onStop={handleStop}
        />
      </div>
    </div>
  );
};

export default DiceView;
