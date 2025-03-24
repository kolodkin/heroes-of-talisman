import styles from './CharachterSelect.module.css'
import className from 'classnames'

import { DiceIcon, HeartIcon } from './Icons';

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : '');
import lang from './he'

const CharachterCard = ({ name, character }) => {
    const nameStr = lang.charachterNames[name];

    return (
        <div className={className(styles.charachter, 'text-2xl')}>
            <img src={`/images/${name}.png`} alt={name} style={{ width: '200px', height: '200px' }} />
            <p className="align-text-center w-full">{nameStr} דרגה {character.level}</p>
            <div className='flex items-center space-x-1'>
                {[...Array(character.dice).keys()].map((i) => (<DiceIcon color="white" fill="black" size={"20px"} key={i} />))}
                <span>{signStr(character.attack)}</span>
            </div>
            <div className='flex items-center'>
                {/* {[...Array(character.health).keys()].map((i) => (<HeartIcon color="red" size={"20px"} key={i} />))} */}
                <HeartIcon color="red" size={"20px"} />
                <span>[{character.health}/{character.max_health}]</span>
            </div>
        </div>
    )
}


const CharacterSelect = ({ characters, handleSelect }) => {
    return (
        <div className='character-select flex justify-center space-x-3'>
            {Object.entries(characters).map(([name, character]) => (
                <CharachterCard key={name} name={name} character={character} />
            ))}
        </div>
    )
}


export default CharacterSelect