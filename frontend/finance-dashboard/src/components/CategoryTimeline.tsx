import { useEffect, useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { fetchTimelineByCategory } from "../components/api";

const categories = [
  "Dining",
  "Groceries",
  "Subscriptions",
  "Purchases",
  "Necessities",
  "Transportation",
];

export default function CategoryTimeline() {
  const [data, setData] = useState<any[]>([]);
  const [category, setCategory] = useState("Dining");

  useEffect(() => {
    fetchTimelineByCategory(category).then(setData);
  }, [category]);

  return (
    <div className="w-full">
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="select mb-4"
      >
        {categories.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <div className="h-[260px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="#334155" />
            <XAxis dataKey="posting_date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#34d399" strokeWidth={2} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
