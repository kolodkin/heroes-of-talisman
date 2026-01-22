import React from "react";
import styles from "./FaceCard.module.css";

const FaceCard = ({ faceUp = true, selected = false, onClick, children }) => {
  return (
    <div
      className={`${styles.card} ${!faceUp ? styles["card--face-down"] : ""} ${
        selected ? styles["card--selected"] : ""
      }`}
      onClick={onClick}
    >
      {faceUp ? children : <div className={styles["card-back"]} />}
    </div>
  );
};

export default FaceCard;
