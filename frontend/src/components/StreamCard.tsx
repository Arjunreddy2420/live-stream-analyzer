import { useState } from "react";
import { api, Stream, StreamAnalysis } from "../services/api";
import { formatBitrate, formatFps, formatMs, formatPercent } from "../utils/format";

interface Props {
  stream: Stream;
  analysis: StreamAnalysis | undefined;
  onDeleted: () => void;
  onAnalyzed: (analysis: StreamAnalysis) => void;
}

export function StreamCard({ stream, analysis, onDeleted, onAnalyzed }: Props) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRunAnalysis() {
    setRunning(true);
    setError(null);
    try {
      const result = await api.triggerAnalysis(stream.id);
      onAnalyzed(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setRunning(false);
    }
  }

  async function handleDelete() {
    await api.deleteStream(stream.id);
    onDeleted();
  }

  return (
    <div className="stream-card">
      <div className="stream-card-header">
        <div>
          <div className="name">{stream.name}</div>
          <div className="source-url">{stream.source_url}</div>
        </div>
        <div className="stream-card-actions">
          <span className="badge protocol">{stream.protocol}</span>
          <button onClick={handleRunAnalysis} disabled={running}>
            {running ? "Analyzing…" : "Run Analysis"}
          </button>
          <button className="secondary" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      {error && <p style={{ color: "var(--status-critical)", fontSize: "0.8125rem" }}>{error}</p>}

      {analysis ? (
        <div className="stat-row">
          <div className="stat-tile">
            <div className="label">Video</div>
            <div className="value">
              {analysis.video_codec ?? "—"} {analysis.video_resolution ?? ""}
            </div>
          </div>
          <div className="stat-tile">
            <div className="label">FPS</div>
            <div className="value">{formatFps(analysis.video_fps)}</div>
          </div>
          <div className="stat-tile">
            <div className="label">Bitrate</div>
            <div className="value">{formatBitrate(analysis.video_bitrate)}</div>
          </div>
          <div className="stat-tile">
            <div className="label">Audio</div>
            <div className="value">{analysis.audio_codec ?? "—"}</div>
          </div>
          <div className="stat-tile">
            <div className="label">Packet Loss</div>
            <div className="value">{formatPercent(analysis.packet_loss)}</div>
          </div>
          <div className="stat-tile">
            <div className="label">Jitter</div>
            <div className="value">{formatMs(analysis.jitter_ms)}</div>
          </div>
        </div>
      ) : (
        <p className="no-data">No analysis yet — click &quot;Run Analysis&quot; to probe this stream.</p>
      )}
    </div>
  );
}
