import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const data = [
  { month: "Jan", spend: 400 },
  { month: "Feb", spend: 300 },
  { month: "Mar", spend: 500 },
];

export default function MonthlySpendingChart() {
  return (
    <LineChart width={250} height={150} data={data}>
      <CartesianGrid stroke="#eee" />
      <XAxis dataKey="month" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="spend" stroke="#8884d8" />
    </LineChart>
  );
}
