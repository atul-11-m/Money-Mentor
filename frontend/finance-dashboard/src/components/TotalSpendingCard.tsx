import { useEffect, useState } from "react";
import { fetchTotal, fetchIncome, fetchBalance } from "../components/api";

type Mode = "spending" | "income" | "balance";

export default function TotalSpendingCard() {
  const [mode, setMode] = useState<Mode>("spending");
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (mode === "spending") {
      fetchTotal().then((res) => setValue(Math.abs(res.total_spending)));
    } else if (mode === "income") {
      fetchIncome().then((res) => setValue(res.net_income));
    } else if (mode === "balance") {
      fetchBalance().then((res) => setValue(res.net_balance));
    }
  }, [mode]);

  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#60a5fa" }}>
        ${value.toFixed(2)}
      </div>
      <div style={{ marginTop: "0.5rem" }}>
        <button onClick={() => setMode("spending")}>Spending</button>
        <button onClick={() => setMode("income")}>Income</button>
        <button onClick={() => setMode("balance")}>Balance</button>
      </div>
    </div>
  );
}
