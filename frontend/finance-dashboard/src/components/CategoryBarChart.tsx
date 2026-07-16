import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { fetchCategoryBar } from "../components/api";

export default function CategoryBarChart() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetchCategoryBar().then(setData);
  }, []);

  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="total" fill="#f87171" isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
