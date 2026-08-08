import { FormEvent, useState } from "react";
import { api, StreamCreatePayload } from "../services/api";

interface Props {
  onCreated: () => void;
}

export function AddStreamForm({ onCreated }: Props) {
  const [name, setName] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [protocol, setProtocol] = useState("RTMP");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || !sourceUrl.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      const payload: StreamCreatePayload = { name, source_url: sourceUrl, protocol };
      await api.createStream(payload);
      setName("");
      setSourceUrl("");
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add stream");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="stream-form" onSubmit={handleSubmit}>
      <input placeholder="Stream name" value={name} onChange={(e) => setName(e.target.value)} required />
      <input
        placeholder="rtmp://localhost:1935/live/test"
        value={sourceUrl}
        onChange={(e) => setSourceUrl(e.target.value)}
        required
      />
      <select value={protocol} onChange={(e) => setProtocol(e.target.value)}>
        <option value="RTMP">RTMP</option>
        <option value="SRT">SRT</option>
      </select>
      <button type="submit" disabled={submitting}>
        {submitting ? "Adding…" : "Add Stream"}
      </button>
      {error && (
        <p style={{ gridColumn: "1 / -1", color: "var(--status-critical)", margin: 0, fontSize: "0.8125rem" }}>
          {error}
        </p>
      )}
    </form>
  );
}
