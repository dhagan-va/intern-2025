import type { Stats } from "../types";
interface StatsDisplayProps {
  stats: Stats | null;
}
export const StatsDisplay = ({ stats }: StatsDisplayProps) => {
  return (
    <div>
      <h2>Statistics</h2>
      {stats ? (
        <div>
          <p>Total Requests: {stats.total_requests}</p>
          <p>Average Latency: {stats.average_latency.toFixed(2)} ms</p>
          <p>Successful: {stats.successful_requests}</p>
          <p>Failed: {stats.failed_requests}</p>
          <p>Current RPS: {stats.current_rps}</p>
          {stats.timestamp && <p>Updated: {stats.timestamp}</p>}

          <div>
            <strong>Status Codes:</strong>
            <ul>
              {Object.entries(stats.status_codes).map(([code, count]) => (
                <li key={code}>
                  {code}: {count}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};
