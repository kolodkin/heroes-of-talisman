import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": {
        target: `http://${process.env.VITE_PROXY_URL ?? "localhost"}:8000`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "/api"),
      },
      "/ws": {
        target: `ws://${process.env.VITE_PROXY_URL ?? "localhost"}:8000`,
        ws: true,
        rewriteWsOrigin: true,
      },
    },
  },
});
