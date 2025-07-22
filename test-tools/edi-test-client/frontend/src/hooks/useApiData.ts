import { useState, useEffect } from "react";
import type { Status, Stats } from "../types";

const API_BASE = "http://localhost:5001";

export const useApiData = () => {
  const [status, setStatus] = useState<Status | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);

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

  return { status, stats };
};