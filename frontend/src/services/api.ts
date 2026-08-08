export interface Stream {
  id: number;
  name: string;
  source_url: string;
  protocol: string;
  created_at: string;
  is_active: boolean;
  last_updated: string | null;
}

export interface StreamAnalysis {
  id: number;
  stream_id: number;
  timestamp: string;
  video_codec: string | null;
  video_resolution: string | null;
  video_bitrate: number | null;
  video_fps: number | null;
  audio_codec: string | null;
  audio_bitrate: number | null;
  audio_channels: number | null;
  audio_sample_rate: number | null;
  packet_loss: number | null;
  jitter_ms: number | null;
}

export interface Alert {
  id: number;
  stream_id: number;
  timestamp: string;
  alert_type: string;
  severity: string;
  message: string;
}

export interface StreamCreatePayload {
  name: string;
  source_url: string;
  protocol: string;
}

const API_BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${options?.method ?? "GET"} ${path} failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  listStreams: () => request<Stream[]>("/streams/"),
  createStream: (payload: StreamCreatePayload) =>
    request<Stream>("/streams/", { method: "POST", body: JSON.stringify(payload) }),
  deleteStream: (id: number) => request<void>(`/streams/${id}`, { method: "DELETE" }),

  getLatestAnalysis: (streamId: number) => request<StreamAnalysis>(`/analysis/${streamId}`),
  triggerAnalysis: (streamId: number) =>
    request<StreamAnalysis>(`/analysis/${streamId}/run`, { method: "POST" }),

  listAlerts: (streamId?: number) =>
    request<Alert[]>(`/alerts/${streamId !== undefined ? `?stream_id=${streamId}` : ""}`),
  dismissAlert: (id: number) => request<void>(`/alerts/${id}`, { method: "DELETE" }),
};
