import { useApiCall } from "../hooks/useApiCall";
import type { Status } from "../types";

interface ControlPanelProps {
  status: Status | null;
}
export const ControlPanel = ({ status }: ControlPanelProps) => {
  const { apiCall, message } = useApiCall();
  return (
    <div>
      <h2>Controls</h2>
      <button onClick={() => apiCall("start")} disabled={status?.running}>
        START
      </button>
      <button onClick={() => apiCall("stop")} disabled={!status?.running}>
        STOP
      </button>
      <button onClick={() => apiCall("reset")}>RESET</button>
      {message && <div>{message}</div>}
    </div>
  );
};
