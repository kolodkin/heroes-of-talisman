import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import cStyles from "./Common.module.css";
import classNames from "classnames";

const getImageSize = (url) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.width, height: img.height });
    img.onerror = reject;
    img.src = url;
  });
};

const DrawCard = ({ sendAction, card, drawn, active }) => {
  const { t } = useTranslation();
  const [isNextPhase, setIsNextPhase] = useState(false);
  const [imageSize, setImageSize] = useState(null);
  const [cardSize, setCardSize] = useState(null);

  const imageUrl = "/images/deck_top.png";
  const cardUrl = `/images/cards/${card}.png`;
  const height = 400;

  useEffect(() => {
    getImageSize(imageUrl).then((size) => setImageSize(size));
    getImageSize(cardUrl).then((size) => setCardSize(size));
  }, []);

  useEffect(() => {
    if (drawn) {
      setTimeout(() => {
        setIsNextPhase(true);
      }, 1000);
    }
  }, [drawn]);

  const handleDrawCard = () => {
    if (!active) {
      return;
    }

    if (!drawn) {
      sendAction("card_draw", { card, drawn: true });
    } else if (isNextPhase) {
      sendAction("card_select", { card });
    }
  };

  if (!imageSize || !cardSize) {
    return null; // todo: add loading spinner
  }

  const ifactor = height / imageSize.height;
  const cfactor = height / cardSize.height;
  const iwidth = imageSize.width * ifactor;

  const cardHeight = cardSize.height * cfactor;
  const cardWidth = cardSize.width * cfactor;

  const width = Math.max(iwidth, cardWidth);

  // Calculate offsets to center the card
  const imageXOffset = (width - iwidth) / 2;
  const cardStartXOffset = (width - cardWidth * 0.5) / 2;
  const cardStartYOffset = (height - cardHeight * 0.5) / 2;
  const cardEndXOffset = (width - cardWidth) / 2;

  return (
    <div className="flex flex-col items-center space-y-3">
      <div style={{ width: width, height: height }}>
        <svg viewBox={`0 0 ${width} ${height}`} xmlns="http://www.w3.org/2000/svg">
          {/* Deck */}
          <image
            href={imageUrl}
            width={iwidth}
            height={height}
            opacity={!drawn ? "1" : "0"}
            x="0"
            y="0"
            style={{
              transform: `translate(${imageXOffset}px, 0px)`,
              transition: "opacity 1s 0.3s ease-in",
            }}
          />
          {/* Card */}
          <image
            href={cardUrl}
            width={cardWidth}
            height={cardHeight}
            opacity={!drawn ? "0" : "1"}
            style={{
              transform: !drawn
                ? `translate(${cardStartXOffset}px, ${cardStartYOffset}px) scale(0.5)`
                : `translate(${cardEndXOffset}px, 0px) scale(1)`,
              transition: "transform 1s 0.3s ease-in, opacity 0.8s ease-in",
            }}
          />
        </svg>
      </div>
      <div
        style={{
          maxHeight: drawn ? "500px" : "0", // auto can't be animated, using value bigger than expected element height
          overflow: "hidden",
          transition: "max-height 1s 0.3s ease-in-out",
        }}
      >
        <div className="text-xl font-bold">{t(`cards.${card}`)}</div>
        <div>{t(`cards.${card}_desc`)}</div>
      </div>
      <button
        className={classNames(" text-white rounded relative overflow-hidden", cStyles.gamebtn)}
        onClick={handleDrawCard}
        style={{ transition: "width 0.5s ease-in-out" }}
      >
        <span style={{ opacity: 0 }}>{drawn ? t("draw_card.draw") : t("draw_card.drawen")}</span>
        <span
          className={`absolute inset-0 flex items-center justify-center`}
          style={{
            opacity: drawn ? 0 : 1,
            transition: "opacity 0.5s ease-in-out",
          }}
        >
          {t("draw_card.draw")}
        </span>
        <span
          className={`absolute inset-0 flex items-center justify-center`}
          style={{
            opacity: drawn ? 1 : 0,
            transition: "opacity 0.5s 0.5s ease-in-out",
          }}
        >
          {t("draw_card.continue")}
        </span>
      </button>
    </div>
  );
};

export default DrawCard;
