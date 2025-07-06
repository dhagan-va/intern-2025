import "./App.css";
import { useState, useEffect } from "react";
import { StatusDisplay } from "./components/StatusDisplay";
import { ConfigMenu } from "./components/ConfigMenu";
import { StatsDisplay } from "./components/StatsDisplay";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useApiCall } from "./hooks/useApiCall";
import { ControlPanel } from "./components/ControlPanel";

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

  const statusCodeData = stats
    ? Object.entries(stats.status_codes).map(([code, count]) => ({
        code,
        count,
      }))
    : [];

  return (
    <div>
      <h1>EDI Test Client Dashboard</h1>
      <StatusDisplay status={status} />
      <ControlPanel status={status} />
      <ConfigMenu />
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

      <StatsDisplay stats={stats} />
    </div>
  );
}

export default App;
