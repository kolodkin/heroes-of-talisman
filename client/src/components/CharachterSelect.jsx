import { useState } from 'react';
import className from 'classnames'
import { notify, enotify } from '../utils/notify';

import styles from './CharachterSelect.module.css'
import { DiceIcon, HeartIcon } from './Icons';

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : '');
import lang from './he'

const CharachterCard = ({ active, name, character, isSelected, onClick }) => {
    const nameStr = lang.charachterNames[name];

    return (
        <div
            className={className({ [styles.selected]: isSelected, [styles.active]: active }, styles.charachter, 'text-2xl')}
            onClick={onClick}
        >
            <img src={`/images/${name}.png`} alt={name} style={{ minWidth: '200px', width: '200px', height: '200px' }} />
            <p className="align-text-center w-full">{nameStr} דרגה {character.level}</p>
            <div className='flex items-center space-x-1'>
                {[...Array(character.dice).keys()].map((i) => (<DiceIcon color="white" fill="black" size={"20px"} key={i} />))}
                <span>{signStr(character.attack)}</span>
            </div>
            <div className='flex items-center'>
                <HeartIcon color="red" size={"20px"} />
                <span>[{character.health}/{character.max_health}]</span>
            </div>
        </div>
    )
}

const CharacterSelect = ({ characters, sendAction, active }) => {
    const [selectedCharacter, setSelectedCharacter] = useState(null);

    const handleCharacterClick = (name) => {
        setSelectedCharacter(name);
        // notify(`selected ${lang.charachterNames[name]}`);
    };

    const handleSubmit = () => {
        if (selectedCharacter) {
            sendAction(selectedCharacter);
        } else {
            notify('Please select a character.');
        }
    };

    return (
        <div className='character-select flex flex-col items-center space-y-3'>
            <div className='flex justify-center space-x-3 mb-8'>
                {Object.entries(characters).map(([name, character]) => (
                    <CharachterCard
                        active={active}
                        key={name}
                        name={name}
                        character={character}
                        isSelected={name === selectedCharacter}
                        onClick={() => handleCharacterClick(name)}
                    />
                ))}
            </div>
            <button
                className={className({ [styles.active]: active }, styles.charachter, 'text-2xl', 'rounded')}
                onClick={handleSubmit}
                disabled={!active}
            >
                <p>{lang.character_select.submit}</p>
            </button>
        </div>
    )
}

export default CharacterSelect