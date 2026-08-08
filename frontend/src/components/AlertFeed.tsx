import { Alert } from "../services/api";
import { formatTimestamp } from "../utils/format";

const SEVERITY_COLOR: Record<string, string> = {
  critical: "var(--status-critical)",
  serious: "var(--status-serious)",
  warning: "var(--status-warning)",
  info: "var(--status-good)",
};

interface Props {
  alerts: Alert[];
}

export function AlertFeed({ alerts }: Props) {
  if (alerts.length === 0) {
    return <p className="empty-state">No alerts.</p>;
  }

  return (
    <div className="alert-list">
      {alerts.map((alert) => (
        <div className="alert-item" key={alert.id}>
          <span
            className="severity-dot"
            style={{ background: SEVERITY_COLOR[alert.severity] ?? "var(--text-muted)" }}
          />
          <span className="message">{alert.message}</span>
          <span className="timestamp">{formatTimestamp(alert.timestamp)}</span>
        </div>
      ))}
    </div>
  );
}
