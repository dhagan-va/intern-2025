import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { Stats } from "../types";

interface StatusCodeChartProps {
  stats: Stats | null;
}

export const StatusCodeChart = ({ stats }: StatusCodeChartProps) => {
  const statusCodeData = stats
    ? Object.entries(stats.status_codes).map(([code, count]) => ({
        code,
        count,
      }))
    : [];

  if (statusCodeData.length === 0) {
    return null;
  }

  return (
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
  );
};