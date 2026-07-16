import { useEffect, useState } from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import { fetchSummary } from "../components/api";

const COLORS = ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa", "#f472b6"];

const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
  if (percent < 0.04) return null; // skip tiny slices to avoid overlap
  const RADIAN = Math.PI / 180;
  const radius = outerRadius + 24;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text
      x={x}
      y={y}
      fill="#e2e8f0"
      textAnchor={x > cx ? "start" : "end"}
      dominantBaseline="central"
      fontSize={12}
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default function TopCategoriesPie() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetchSummary().then(setData);
  }, []);

  return (
    <ResponsiveContainer width="100%" height={340}>
      <PieChart margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
        <Pie
          data={data}
          dataKey="total"
          nameKey="category"
          cx="50%"
          cy="50%"
          outerRadius={100}
          labelLine={false}
          label={renderLabel}
          isAnimationActive={false}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, "Total"]} />
        <Legend
          iconType="circle"
          iconSize={10}
          wrapperStyle={{ paddingTop: "12px", paddingBottom: "8px", fontSize: "13px" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
