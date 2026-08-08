import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// BACKEND_HOST lets the same config work both for local `npm run dev`
// (backend on localhost) and inside Docker Compose (backend on the
// "backend" service hostname).
const backendHost = process.env.BACKEND_HOST ?? "localhost";

// Dev server proxies API/WebSocket calls to the backend so the frontend
// can use relative paths (/api/..., /ws) in both dev and prod.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/api": `http://${backendHost}:8000`,
      "/ws": {
        target: `ws://${backendHost}:8000`,
        ws: true,
      },
    },
  },
});
