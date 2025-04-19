import className from 'classnames';
import { notify } from '../utils/notify';

import styles from './CharacterSelect.module.css';
import commonStyles from './Common.module.css';
import { DiceIcon, HeartIcon } from './Icons';

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : '');
import lang from './he'

const CharacterCard = ({ name, character, isSelected, onClick }) => {
    const nameStr = lang.characterNames[name];

    return (
        <div
            className={className({ [commonStyles.selected]: isSelected }, commonStyles.gamebtn, styles.character, 'text-2xl')}
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

const CharacterSelect = ({ characters, sendAction, active, selectedCharacter = null }) => {
    const handleCharacterClick = (name) => {
        if (!active) {
            return;
        }

        sendAction('character_select', { character: name });
        // notify(`selected ${lang.characterNames[name]}`);
    };

    const handleSubmit = () => {
        if (!active) {
            return;
        }

        if (selectedCharacter) {
            sendAction('character_selected', { character: selectedCharacter });
        } else {
            notify('character_select.select_character');
        }
    };

    return (
        <div className='flex flex-col items-center space-y-3'>
            <div className='flex justify-center space-x-3 mb-8'>
                {Object.entries(characters).map(([name, character]) => (
                    <CharacterCard
                        key={name}
                        name={name}
                        character={character}
                        isSelected={name === selectedCharacter}
                        onClick={() => handleCharacterClick(name)}
                    />
                ))}
            </div>
            <button
                className={className(commonStyles.gamebtn, styles.character, 'text-2xl', 'rounded')}
                onClick={handleSubmit}
            >
                <p>{lang.character_select.submit}</p>
            </button>
        </div>
    )
}

export default CharacterSelect