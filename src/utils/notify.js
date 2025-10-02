import { toast } from "react-toastify";
import i18n from "../i18n";

export const notify = (key) => {
  const msg = i18n.t(key);
  console.log("notify", key, msg);
  toast(msg);
};

export const enotify = (key, params = {}) => {
  const msg = i18n.t(key, params);
  console.error("enotify", key, msg);
  toast.error(msg);
};
