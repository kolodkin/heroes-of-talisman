export default function printf(format, ...args) {
    let i = 0;
    return format.replace(/%[sdfo]/g, match => {
        if (i >= args.length) return match;
        switch (match) {
            case "%s": return String(args[i++]);
            case "%d": return parseInt(args[i++], 10);
            case "%f": return parseFloat(args[i++]);
            case "%o": return JSON.stringify(args[i++]);
            default: return match;
        }
    });
}
