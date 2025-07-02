import "./App.css";
import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_BASE = "http://localhost:5001";

interface Status {
  running: boolean;
  rps: number;
  transaction: number;
  threads: number;
  endpoint: string;
}

interface Stats {
  total_requests: number;
  average_latency: number;
  status_codes: Record<string, number>;
  successful_requests: number;
  failed_requests: number;
  current_rps: number;
  timestamp?: string;
}

function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [rpsInput, setRpsInput] = useState("");
  const [transactionInput, setTransactionInput] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, statsRes] = await Promise.all([
          fetch(`${API_BASE}/status`),
          fetch(`${API_BASE}/stats`),
        ]);

        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setStatus(statusData);
          setRpsInput(statusData.rps.toString());
          setTransactionInput(statusData.transaction.toString());
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const apiCall = async (endpoint: string, method = "POST", body?: object) => {
    try {
      const response = await fetch(`${API_BASE}/${endpoint}`, {
        method,
        headers: body ? { "Content-Type": "application/json" } : {},
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await response.json();
      setMessage(data.message || data.error);
    } catch (error) {
      console.error(`Error with ${endpoint}:`, error);
      setMessage(`Error with ${endpoint}`);
    }
  };

  const statusCodeData = stats
    ? Object.entries(stats.status_codes).map(([code, count]) => ({
        code,
        count,
      }))
    : [];

  return (
    <div>
      <h1>EDI Test Client Dashboard</h1>

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
          <p>Loading...</p>
        )}
      </div>

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

      <div>
        <h2>Configuration</h2>
        <div>
          <label>RPS:</label>
          <input
            type="number"
            step="0.1"
            value={rpsInput}
            onChange={(e) => setRpsInput(e.target.value)}
          />
          <button
            onClick={() =>
              apiCall("rps", "POST", { rps: parseFloat(rpsInput) })
            }
          >
            Update
          </button>
        </div>

        <div>
          <label>Transaction:</label>
          <select
            value={transactionInput}
            onChange={(e) => setTransactionInput(e.target.value)}
          >
            <option value="270">270</option>
            <option value="276">276</option>
            <option value="278">278</option>
          </select>
          <button
            onClick={() =>
              apiCall("transaction", "POST", {
                transaction: parseInt(transactionInput),
              })
            }
          >
            Update
          </button>
        </div>
      </div>

      {statusCodeData.length > 0 && (
        <div>
          <h2>Status Code Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusCodeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="code" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

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
    </div>
  );
}

export default App;
