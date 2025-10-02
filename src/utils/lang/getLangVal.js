import lang from "./he";

export const getLangVal = (key) => {
  const path = key.split(".");
  let val = lang;
  for (let p of path) {
    val = val[p];
  }
  return val;
};
