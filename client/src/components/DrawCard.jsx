import { useState } from 'react';
import className from 'classnames';
import { notify } from '../utils/notify';

import styles from './DrawCard.module.css';

const DrawCard = ({ sendAction, active }) => {
    const [isDrawing, setIsDrawing] = useState(false);

    const handleDrawCard = () => {
        setIsDrawing(true);
    };

    return (
        <div className="flex flex-col items-center space-y-3">
            <div className="w-100 h-100">
                <svg
                    viewBox="0 0 200 200"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    {/* Deck */}
                    <image
                        href="/images/deck_top.png"
                        width="200"
                        height="200"
                        x="0"
                        y="0"
                    />
                    {/* Card */}
                    <image
                        href="/images/card1.png"
                        width="200"
                        height="200"
                        opacity={!isDrawing ? "0" : "1"}
                        style={{
                            transform: !isDrawing ?
                                "translate(60px, 70px) scale(0.4, 0.45)" :
                                "translate(0px, 0px) scale(1)",
                            transition: 'transform 1s 0.5s ease-in, opacity 0.8s ease-in',
                        }}
                    />
                </svg>

            </div>
            <button
                className="px-4 py-2 bg-blue-500 text-white rounded"
                onClick={handleDrawCard}
                disabled={isDrawing}
            >
                {isDrawing ? 'Drawing...' : 'Draw Card'}
            </button>
        </div>
    );
};

export default DrawCard;