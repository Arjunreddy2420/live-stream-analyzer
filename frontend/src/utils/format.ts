export function formatBitrate(kbps: number | null): string {
  if (kbps === null) return "—";
  if (kbps >= 1000) return `${(kbps / 1000).toFixed(2)} Mbps`;
  return `${kbps} kbps`;
}

export function formatFps(fps: number | null): string {
  return fps === null ? "—" : `${fps.toFixed(1)} fps`;
}

export function formatPercent(value: number | null, digits = 2): string {
  return value === null ? "—" : `${value.toFixed(digits)}%`;
}

export function formatMs(value: number | null): string {
  return value === null ? "—" : `${value.toFixed(2)} ms`;
}

export function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString();
}
