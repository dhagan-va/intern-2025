import "./App.css";
import { useState, useEffect } from "react";

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

  return (
<></> );
}

export default App;
