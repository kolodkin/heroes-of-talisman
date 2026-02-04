export const DiceIcon = ({ size, color, fill }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} xmlns="http://www.w3.org/2000/svg">
    <rect width="24" height="24" rx="4" />
    <circle cx="8" cy="8" r="1.5" fill={color} />
    <circle cx="16" cy="8" r="1.5" fill={color} />
    <circle cx="8" cy="16" r="1.5" fill={color} />
    <circle cx="16" cy="16" r="1.5" fill={color} />
  </svg>
);

export const HeartIcon = ({ size, color }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} xmlns="http://www.w3.org/2000/svg">
    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
  </svg>
);

export const RerollIcon = ({ size, color, fill }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" data-icon-reroll>
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
  </svg>
);

export const SkipTurnIcon = ({ size, color, fill }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    data-icon-skip-turn
  >
    <circle cx="12" cy="12" r="10" fill={fill} stroke={color} strokeWidth="2" />
    <path d="M8 8 L16 12 L8 16 Z" fill={color} stroke="none" />
    <rect x="16" y="8" width="2" height="8" fill={color} />
  </svg>
);

export const NotAliveIcon = ({ size, color, fill }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    data-icon-not-alive
  >
    <circle cx="12" cy="12" r="10" fill={fill} stroke={color} strokeWidth="2" />
    <path d="M8 8 L16 16 M16 8 L8 16" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);

export const ArmorIcon = ({ size, color, fill }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" data-icon-armor>
    <path
      d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
      fill={fill}
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const SwordIcon = ({ size, color, fill }) => (
  <svg width={size} height={size} viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" data-icon-sword>
    <path
      d="M19.75 14.438c59.538 112.29 142.51 202.35 232.28 292.718l3.626 3.75.063-.062c21.827 21.93 44.04 43.923 66.405 66.25-18.856 14.813-38.974 28.2-59.938 40.312l28.532 28.53 68.717-68.717c42.337 27.636 76.286 63.646 104.094 105.81l28.064-28.06c-42.47-27.493-79.74-60.206-106.03-103.876l68.936-68.938-28.53-28.53c-11.115 21.853-24.413 42.015-39.47 60.593-43.852-43.8-86.462-85.842-130.125-125.47-.224-.203-.432-.422-.656-.625C183.624 122.75 108.515 63.91 19.75 14.437zm471.875 0c-83.038 46.28-154.122 100.78-221.97 161.156l22.814 21.562 56.81-56.812 13.22 13.187-56.438 56.44 24.594 23.186c61.802-66.92 117.6-136.92 160.97-218.72zm-329.53 125.906 200.56 200.53a402.965 402.965 0 0 1-13.405 13.032L148.875 153.53l13.22-13.186zm-76.69 113.28-28.5 28.532 68.907 68.906c-26.29 43.673-63.53 76.414-106 103.907l28.063 28.06c27.807-42.164 61.758-78.174 104.094-105.81l68.718 68.717 28.53-28.53c-20.962-12.113-41.08-25.5-59.937-40.313 17.865-17.83 35.61-35.433 53.157-52.97l-24.843-25.655-55.47 55.467c-4.565-4.238-9.014-8.62-13.374-13.062l55.844-55.844-24.53-25.374c-18.28 17.856-36.602 36.06-55.158 54.594-15.068-18.587-28.38-38.758-39.5-60.625z"
      fill={fill}
      stroke={color}
      strokeWidth="8"
    />
  </svg>
);
