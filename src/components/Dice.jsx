/**
 * Dice Component
 *
 * Visual dice component with true 3D cube rotation
 * - Fixed Size: 80x80px
 * - Props:
 *   - value: Final dice value to display (1-6)
 *   - rollDuration: Animation duration in milliseconds
 *   - tilt: Base tilt angle for natural look (default: 5 degrees)
 *   - tiltMargin: Random margin added to base tilt (default: 5 degrees)
 * - Animation:
 *   - During roll: 3D cube rotation effect
 *   - After duration: Shows final value face with random tilt and stops animation
 * - Styling: CSS 3D cube with 6 faces, each showing different dice dots
 */
import React, { useState, useEffect } from "react";
import className from "classnames";
import styles from "./Dice.module.css";

const DiceDots = ({ value }) => {
  const dots = [];

  // Generate dots based on value
  if (value === 1) {
    dots.push(<div key="center" className={styles.dot} style={{ gridArea: "2 / 2 / 3 / 3" }} />);
  } else if (value === 2) {
    dots.push(<div key="tl" className={styles.dot} style={{ gridArea: "1 / 1 / 2 / 2" }} />);
    dots.push(<div key="br" className={styles.dot} style={{ gridArea: "3 / 3 / 4 / 4" }} />);
  } else if (value === 3) {
    dots.push(<div key="tl" className={styles.dot} style={{ gridArea: "1 / 1 / 2 / 2" }} />);
    dots.push(<div key="center" className={styles.dot} style={{ gridArea: "2 / 2 / 3 / 3" }} />);
    dots.push(<div key="br" className={styles.dot} style={{ gridArea: "3 / 3 / 4 / 4" }} />);
  } else if (value === 4) {
    dots.push(<div key="tl" className={styles.dot} style={{ gridArea: "1 / 1 / 2 / 2" }} />);
    dots.push(<div key="tr" className={styles.dot} style={{ gridArea: "1 / 3 / 2 / 4" }} />);
    dots.push(<div key="bl" className={styles.dot} style={{ gridArea: "3 / 1 / 4 / 2" }} />);
    dots.push(<div key="br" className={styles.dot} style={{ gridArea: "3 / 3 / 4 / 4" }} />);
  } else if (value === 5) {
    dots.push(<div key="tl" className={styles.dot} style={{ gridArea: "1 / 1 / 2 / 2" }} />);
    dots.push(<div key="tr" className={styles.dot} style={{ gridArea: "1 / 3 / 2 / 4" }} />);
    dots.push(<div key="center" className={styles.dot} style={{ gridArea: "2 / 2 / 3 / 3" }} />);
    dots.push(<div key="bl" className={styles.dot} style={{ gridArea: "3 / 1 / 4 / 2" }} />);
    dots.push(<div key="br" className={styles.dot} style={{ gridArea: "3 / 3 / 4 / 4" }} />);
  } else if (value === 6) {
    dots.push(<div key="tl" className={styles.dot} style={{ gridArea: "1 / 1 / 2 / 2" }} />);
    dots.push(<div key="tr" className={styles.dot} style={{ gridArea: "1 / 3 / 2 / 4" }} />);
    dots.push(<div key="ml" className={styles.dot} style={{ gridArea: "2 / 1 / 3 / 2" }} />);
    dots.push(<div key="mr" className={styles.dot} style={{ gridArea: "2 / 3 / 3 / 4" }} />);
    dots.push(<div key="bl" className={styles.dot} style={{ gridArea: "3 / 1 / 4 / 2" }} />);
    dots.push(<div key="br" className={styles.dot} style={{ gridArea: "3 / 3 / 4 / 4" }} />);
  }

  return dots;
};

// Define rotation angles for each face (outside component to avoid recreation)
const FACE_ROTATIONS = {
  1: { x: 0, y: 0 },
  2: { x: 0, y: 90 },
  3: { x: 0, y: 180 },
  4: { x: 0, y: -90 },
  5: { x: 90, y: 0 },
  6: { x: -90, y: 0 },
};

const Dice = ({ value, rollDuration = 2000, tilt = 5, tiltMargin = 5 }) => {
  const [isRolling, setIsRolling] = useState(rollDuration > 0);
  const [rotation, setRotation] = useState(FACE_ROTATIONS[value] || FACE_ROTATIONS[1]);

  useEffect(() => {
    const baseRotation = FACE_ROTATIONS[value] || FACE_ROTATIONS[1];

    // Add random tilt for natural look
    const tiltX = (Math.random() < 0.5 ? 1 : -1) * (tilt + Math.random() * tiltMargin);
    const tiltY = (Math.random() < 0.5 ? 1 : -1) * (tilt + Math.random() * tiltMargin);

    const targetRotation = {
      x: baseRotation.x + tiltX,
      y: baseRotation.y + tiltY,
    };

    if (rollDuration <= 0) {
      setIsRolling(false);
      setRotation(targetRotation);
      return;
    }

    setIsRolling(true);

    // Random rotations during rolling
    const interval = setInterval(() => {
      setRotation({
        x: Math.random() * 360,
        y: Math.random() * 360,
      });
    }, 100);

    // Stop rolling and show final value
    const timeout = setTimeout(() => {
      clearInterval(interval);
      setIsRolling(false);
      setRotation(targetRotation);
    }, rollDuration);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [value, rollDuration, tilt, tiltMargin]);

  return (
    <div className={styles.diceContainer}>
      <div
        className={className(styles.dice, { [styles.rolling]: isRolling })}
        style={{
          transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`,
          transition: isRolling ? "none" : "transform 0.5s ease-out",
        }}
      >
        {/* Face 1 - Front */}
        <div className={className(styles.face, styles.front)}>
          <DiceDots value={1} />
        </div>
        {/* Face 2 - Right */}
        <div className={className(styles.face, styles.right)}>
          <DiceDots value={2} />
        </div>
        {/* Face 3 - Back */}
        <div className={className(styles.face, styles.back)}>
          <DiceDots value={3} />
        </div>
        {/* Face 4 - Left */}
        <div className={className(styles.face, styles.left)}>
          <DiceDots value={4} />
        </div>
        {/* Face 5 - Top */}
        <div className={className(styles.face, styles.top)}>
          <DiceDots value={5} />
        </div>
        {/* Face 6 - Bottom */}
        <div className={className(styles.face, styles.bottom)}>
          <DiceDots value={6} />
        </div>
      </div>
    </div>
  );
};

export default Dice;
