import { useEffect, useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { fetchTimeline } from "../components/api";

export default function MonthlySpendingChart() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetchTimeline().then(setData);
  }, []);

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid stroke="#334155" />
        <XAxis dataKey="posting_date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="total" stroke="#60a5fa" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
