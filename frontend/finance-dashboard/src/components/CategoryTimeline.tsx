import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { fetchTimelineByCategory } from "../components/api";

const categories = [
  "Dining",
  "Groceries",
  "Subscriptions",
  "Purchases",
  "Necessities",
  "Transportation"
];

export default function CategoryTimeline() {
  const [data, setData] = useState<any[]>([]);
  const [category, setCategory] = useState("Dining");

  useEffect(() => {
    fetchTimelineByCategory(category).then(setData);
  }, [category]);

  return (
    <div style={{ width: "100%" }}>
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        style={{ marginBottom: "1rem", padding: "0.25rem" }}
      >
        {categories.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>

      <LineChart width={500} height={250} data={data}>
        <CartesianGrid stroke="#334155" />
        <XAxis dataKey="posting_date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="total" stroke="#34d399" strokeWidth={2} />
      </LineChart>
    </div>
  );
}
