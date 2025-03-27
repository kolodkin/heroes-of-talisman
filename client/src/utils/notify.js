import { toast } from 'react-toastify';
import lang from '../components/he';
import printf from './printf';

const getVal = (key) => {
    const path = key.split('.');
    let val = lang;
    for (let p of path){
        val = val[p];
    }
    return val;
}

export const notify = (key) => {
    let msg = getVal(key);
    console.log('notify', key, msg);
    toast(msg);
}

export const enotify = (key, ...args) => {
    let msg = getVal(key);
    msg = printf(msg, ...args);
    console.error('enotify', key, msg);
    toast.error(msg);
}
