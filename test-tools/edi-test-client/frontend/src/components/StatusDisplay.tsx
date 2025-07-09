import type { Status } from "../types";

interface StatusDisplayProps {
  status: Status | null;
}
export const StatusDisplay = ({ status }: StatusDisplayProps) => {
  return (
    <div>
      <h2>Status</h2>
      {status ? (
        <div>
          <p>Running: {status.running ? "Yes" : "No"}</p>
          <p>RPS: {status.rps}</p>
          <p>Transaction: {status.transaction}</p>
          <p>Threads: {status.threads}</p>
          <p>Endpoint: {status.endpoint}</p>
        </div>
      ) : (
        <p> Loading...</p>
      )}
    </div>
  );
};