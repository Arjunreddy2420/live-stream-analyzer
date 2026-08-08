import { useCallback, useEffect, useState } from "react";
import { AddStreamForm } from "../components/AddStreamForm";
import { AlertFeed } from "../components/AlertFeed";
import { StreamCard } from "../components/StreamCard";
import { Alert, api, Stream, StreamAnalysis } from "../services/api";
import { connectWebSocket } from "../services/websocket";

export function Dashboard() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [analyses, setAnalyses] = useState<Record<number, StreamAnalysis>>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [connected, setConnected] = useState(false);

  const refreshStreams = useCallback(async () => {
    setStreams(await api.listStreams());
  }, []);

  const refreshAlerts = useCallback(async () => {
    setAlerts(await api.listAlerts());
  }, []);

  useEffect(() => {
    refreshStreams();
    refreshAlerts();
  }, [refreshStreams, refreshAlerts]);

  useEffect(() => {
    setConnected(true);
    const disconnect = connectWebSocket((message) => {
      setAnalyses((prev) => ({ ...prev, [message.stream_id]: message.analysis }));
      if (message.alerts.length > 0) {
        setAlerts((prev) => [...message.alerts, ...prev]);
      }
    });
    return () => {
      disconnect();
      setConnected(false);
    };
  }, []);

  function handleStreamDeleted(streamId: number) {
    refreshStreams();
    setAnalyses((prev) => {
      const next = { ...prev };
      delete next[streamId];
      return next;
    });
  }

  return (
    <div>
      <div className="panel">
        <h2>Add Stream</h2>
        <AddStreamForm onCreated={refreshStreams} />
      </div>

      <div className="panel">
        <h2>Streams ({streams.length})</h2>
        {streams.length === 0 ? (
          <p className="empty-state">No streams registered yet — add one above to get started.</p>
        ) : (
          <div className="stream-list">
            {streams.map((stream) => (
              <StreamCard
                key={stream.id}
                stream={stream}
                analysis={analyses[stream.id]}
                onDeleted={() => handleStreamDeleted(stream.id)}
                onAnalyzed={(analysis) => setAnalyses((prev) => ({ ...prev, [stream.id]: analysis }))}
              />
            ))}
          </div>
        )}
      </div>

      <div className="panel">
        <h2>
          Recent Alerts
          <span className={connected ? "conn-status connected" : "conn-status"}>
            {connected ? "● live" : "○ connecting"}
          </span>
        </h2>
        <AlertFeed alerts={alerts} />
      </div>
    </div>
  );
}
