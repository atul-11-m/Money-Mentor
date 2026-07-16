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

  const modes: Mode[] = ["spending", "income", "balance"];

  return (
    <div className="text-center">
      <div className="text-4xl font-bold text-accent">${value.toFixed(2)}</div>
      <div className="mt-3 flex justify-center gap-2">
        {modes.map((m) => (
          <button
            key={m}
            className={`btn ${mode === m ? "active" : ""}`}
            onClick={() => setMode(m)}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
}
