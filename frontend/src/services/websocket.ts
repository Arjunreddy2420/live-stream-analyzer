import type { Alert, StreamAnalysis } from "./api";

export interface AnalysisMessage {
  type: "analysis";
  stream_id: number;
  analysis: StreamAnalysis;
  alerts: Alert[];
}

type Listener = (message: AnalysisMessage) => void;

/**
 * Opens a WebSocket to the backend's /ws endpoint and invokes `onMessage` for
 * every broadcast analysis update. Returns a cleanup function to close it.
 */
export function connectWebSocket(onMessage: Listener): () => void {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      if (message?.type === "analysis") {
        onMessage(message as AnalysisMessage);
      }
    } catch {
      // ignore malformed messages
    }
  };

  return () => socket.close();
}
