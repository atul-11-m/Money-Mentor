import { PieChart, Pie, Cell, Tooltip } from "recharts";

const data = [
  { name: "Food", value: 400 },
  { name: "Rent", value: 700 },
  { name: "Travel", value: 200 },
];

const COLORS = ["#0088FE", "#00C49F", "#FFBB28"];

export default function TopCategoriesPie() {
  return (
    <PieChart width={250} height={150}>
      <Pie data={data} dataKey="value" outerRadius={60} fill="#8884d8" label>
        {data.map((_, i) => (
          <Cell key={i} fill={COLORS[i % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  );
}
