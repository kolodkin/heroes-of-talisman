import { toast as realToast, ToastContainer as RealToastContainer } from "react-toastify";

const isE2E = import.meta.env.VITE_E2E === "true";

export const toast = isE2E
  ? Object.assign((msg) => console.log("toast", msg), {
      error: (msg) => console.log("toast.error", msg),
      success: (msg) => console.log("toast.success", msg),
    })
  : realToast;

export const ToastContainer = isE2E ? () => null : RealToastContainer;
