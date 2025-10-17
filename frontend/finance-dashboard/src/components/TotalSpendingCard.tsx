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
      <div style={{ marginTop: "0.5rem", display: "flex", gap: 8, justifyContent: "center" }}>
        <button className={`btn ${mode === "spending" ? "active" : ""}`} onClick={() => setMode("spending")}>Spending</button>
        <button className={`btn ${mode === "income" ? "active" : ""}`} onClick={() => setMode("income")}>Income</button>
        <button className={`btn ${mode === "balance" ? "active" : ""}`} onClick={() => setMode("balance")}>Balance</button>
      </div>
    </div>
  );
}
