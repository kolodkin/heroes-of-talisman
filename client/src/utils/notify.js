import { toast } from 'react-toastify';

export const notify = (msg) => {
    console.log(msg);
    toast(msg);
}

export const enotify = (msg) => {
    console.error(msg);
    toast.error(msg);
}
