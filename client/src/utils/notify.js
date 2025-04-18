import { toast } from 'react-toastify';
import { getLangVal } from './lang';
import printf from './printf';


export const notify = (key) => {
    let msg = getLangVal(key);
    console.log('notify', key, msg);
    toast(msg);
}

export const enotify = (key, ...args) => {    
    let msg = getLangVal(key);
    msg = printf(msg, ...args);
    console.error('enotify', key, msg);
    toast.error(msg);
}
