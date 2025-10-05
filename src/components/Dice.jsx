/**
 * Dice Component
 *
 * Visual dice component with 3D rotation animation using SVG
 * - Fixed Size: 80x80px
 * - Props:
 *   - value: Final dice value to display (1-6)
 *   - rollDuration: Animation duration in milliseconds
 * - Animation:
 *   - During roll: 3D rotation effect with random face changes every 100ms
 *   - After duration: Shows final value and stops animation
 * - Styling: SVG-based dice with dots representing values
 */
import React, { useState, useEffect } from "react";
import className from "classnames";
import styles from "./Dice.module.css";

const DiceFace = ({ value }) => {
  const dots = [];

  // Define dot positions for each value
  const dotPositions = {
    1: [[50, 50]], // center
    2: [
      [30, 30],
      [70, 70],
    ], // diagonal
    3: [
      [30, 30],
      [50, 50],
      [70, 70],
    ], // diagonal with center
    4: [
      [30, 30],
      [70, 30],
      [30, 70],
      [70, 70],
    ], // corners
    5: [
      [30, 30],
      [70, 30],
      [50, 50],
      [30, 70],
      [70, 70],
    ], // corners + center
    6: [
      [30, 25],
      [70, 25],
      [30, 50],
      [70, 50],
      [30, 75],
      [70, 75],
    ], // two columns
  };

  const positions = dotPositions[value] || dotPositions[1];

  return (
    <svg width="80" height="80" viewBox="0 0 100 100" className={styles.diceSvg}>
      <rect x="5" y="5" width="90" height="90" rx="12" fill="white" stroke="black" strokeWidth="3" />
      {positions.map(([cx, cy], index) => (
        <circle key={index} cx={cx} cy={cy} r="6" fill="black" />
      ))}
    </svg>
  );
};

const Dice = ({ value, rollDuration = 2000 }) => {
  const [isRolling, setIsRolling] = useState(rollDuration > 0);
  const [displayValue, setDisplayValue] = useState(value);

  useEffect(() => {
    if (rollDuration <= 0) {
      setIsRolling(false);
      setDisplayValue(value);
      return;
    }

    setIsRolling(true);

    // Random dice values during rolling
    const interval = setInterval(() => {
      setDisplayValue(Math.floor(Math.random() * 6) + 1);
    }, 100);

    // Stop rolling after duration
    const timeout = setTimeout(() => {
      clearInterval(interval);
      setIsRolling(false);
      setDisplayValue(value);
    }, rollDuration);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [value, rollDuration]);

  return (
    <div className={className(styles.dice, { [styles.rolling]: isRolling })}>
      <DiceFace value={displayValue} />
    </div>
  );
};

export default Dice;
