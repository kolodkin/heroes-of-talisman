const SVGIcon = ({ size, viewBox = "0 0 24 24", dataAttr, children }) => (
  <svg width={size} height={size} viewBox={viewBox} fill="none" xmlns="http://www.w3.org/2000/svg" {...dataAttr}>
    {children}
  </svg>
);

const PNGIcon = ({ src, alt, size, dataAttr }) => (
  <img src={src} alt={alt} {...(size && { width: size, height: size })} {...dataAttr} />
);

export const DiceIcon = ({ size, color, fill }) => (
  <SVGIcon size={size} viewBox="0 0 24 24">
    <rect width="24" height="24" rx="4" fill={fill} />
    <circle cx="8" cy="8" r="1.5" fill={color} />
    <circle cx="16" cy="8" r="1.5" fill={color} />
    <circle cx="8" cy="16" r="1.5" fill={color} />
    <circle cx="16" cy="16" r="1.5" fill={color} />
  </SVGIcon>
);

export const HeartIcon = ({ size, color }) => (
  <SVGIcon size={size} viewBox="0 0 24 24">
    <path
      d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
      fill={color}
    />
  </SVGIcon>
);

export const RerollIcon = ({ size, color, fill }) => (
  <SVGIcon size={size} dataAttr={{ "data-icon-reroll": true }}>
    <circle cx="12" cy="12" r="10" fill={fill} stroke={color} strokeWidth="2" />
    <path
      d="M16 10 L16 6 L12 6 M16 6 C14.5 7.5 13 8.5 11 8.5 C8 8.5 6 6.5 6 4"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
    <path
      d="M8 14 L8 18 L12 18 M8 18 C9.5 16.5 11 15.5 13 15.5 C16 15.5 18 17.5 18 20"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
  </SVGIcon>
);

export const SkipTurnIcon = ({ size, color, fill }) => (
  <SVGIcon size={size} dataAttr={{ "data-icon-skip-turn": true }}>
    <circle cx="12" cy="12" r="10" fill={fill} stroke={color} strokeWidth="2" />
    <path d="M8 8 L16 12 L8 16 Z" fill={color} stroke="none" />
    <rect x="16" y="8" width="2" height="8" fill={color} />
  </SVGIcon>
);

export const NotAliveIcon = ({ size, color, fill }) => (
  <SVGIcon size={size} dataAttr={{ "data-icon-not-alive": true }}>
    <circle cx="12" cy="12" r="10" fill={fill} stroke={color} strokeWidth="2" />
    <path d="M8 8 L16 16 M16 8 L8 16" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
  </SVGIcon>
);

export const ArmorIcon = ({ size }) => (
  <PNGIcon src="/images/cards/metal_armor_icon.png" alt="armor" size={size} dataAttr={{ "data-icon-armor": true }} />
);

export const SwordIcon = ({ size }) => (
  <PNGIcon src="/images/cards/sacred_sword_icon.png" alt="sword" size={size} dataAttr={{ "data-icon-sword": true }} />
);
