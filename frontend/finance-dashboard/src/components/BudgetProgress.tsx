import { useEffect, useState } from "react";
import { fetchIncome, fetchTotal, fetchBalance } from "../components/api";

type Goal = {
  id: string;
  name: string;
  amount: number;
  createdAt: string;
};

export default function BudgetProgress() {
  const [name, setName] = useState("");
  const [amount, setAmount] = useState<number | "">("");
  const [goals, setGoals] = useState<Goal[]>([]);
  const [currentSaved, setCurrentSaved] = useState<number | null>(null);
  const [monthlySavings, setMonthlySavings] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem("goals");
    if (raw) {
      try {
        setGoals(JSON.parse(raw));
      } catch {
        localStorage.removeItem("goals");
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("goals", JSON.stringify(goals));
  }, [goals]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [balanceRes, incomeRes, totalRes] = await Promise.all([
          fetchBalance(),
          fetchIncome(),
          fetchTotal(),
        ]);

        const balance = (balanceRes && (balanceRes.net_balance ?? balanceRes.balance)) ?? null;
        const income = (incomeRes && (incomeRes.net_income ?? incomeRes.income)) ?? null;
        const total = (totalRes && (totalRes.total_spending ?? totalRes.spending)) ?? null;

        if (balance != null) setCurrentSaved(Number(balance));

        if (income != null && total != null) {
          const estimated = Number(income) - Math.abs(Number(total));
          setMonthlySavings(estimated);
        } else {
          setMonthlySavings(null);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function addGoal() {
    if (!name || !amount || Number(amount) <= 0) return;
    const g: Goal = { id: String(Date.now()), name, amount: Number(amount), createdAt: new Date().toISOString() };
    setGoals((s) => [...s, g]);
    setName("");
    setAmount("");
  }

  function removeGoal(id: string) {
    setGoals((s) => s.filter((g) => g.id !== id));
  }

  function moveUp(index: number) {
    if (index <= 0) return;
    setGoals((s) => {
      const a = [...s];
      const tmp = a[index - 1];
      a[index - 1] = a[index];
      a[index] = tmp;
      return a;
    });
  }

  function moveDown(index: number) {
    setGoals((s) => {
      if (index >= s.length - 1) return s;
      const a = [...s];
      const tmp = a[index + 1];
      a[index + 1] = a[index];
      a[index] = tmp;
      return a;
    });
  }

  // Allocation: allocate currentSaved and monthlySavings across goals by priority (array order)
  const totalSaved = currentSaved ?? 0;
  const allocations = goals.map((g) => ({ id: g.id, amount: g.amount, name: g.name, allocatedSaved: 0, allocatedMonthly: 0 }));

  // allocate saved
  let remainingSaved = totalSaved;
  for (const a of allocations) {
    const take = Math.max(0, Math.min(a.amount, remainingSaved));
    a.allocatedSaved = take;
    remainingSaved -= take;
  }

  // allocate monthly savings
  let remainingMonthly = monthlySavings && monthlySavings > 0 ? monthlySavings : 0;
  for (const a of allocations) {
    const need = Math.max(0, a.amount - a.allocatedSaved);
    const take = Math.max(0, Math.min(need, remainingMonthly));
    a.allocatedMonthly = take;
    remainingMonthly -= take;
  }

  return (
    <div style={{ width: "100%" }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
        <input className="input" placeholder="Goal name" value={name} onChange={(e) => setName(e.target.value)} />
        <input className="input" type="number" placeholder="Goal amount" value={amount as any} onChange={(e) => setAmount(e.target.value === "" ? "" : Number(e.target.value))} />
        <button className="btn btn-primary" onClick={addGoal}>Add Goal</button>
      </div>

      {goals.length === 0 && <div style={{ color: "var(--muted)" }}>No goals yet — add one above.</div>}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {allocations.map((a, i) => {
          const percent = a.amount > 0 ? Math.min(100, (a.allocatedSaved / a.amount) * 100) : 0;
          const remaining = Math.max(0, a.amount - a.allocatedSaved);
          const months = remaining > 0 && a.allocatedMonthly > 0 ? Math.ceil(remaining / a.allocatedMonthly) : null;

          return (
            <div key={a.id} style={{ border: "1px solid rgba(255,255,255,0.03)", padding: 12, borderRadius: 8, background: "rgba(255,255,255,0.01)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{a.name}</div>
                  <div style={{ color: "var(--muted)", fontSize: 13 }}>${a.amount.toFixed(2)}</div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <div style={{ textAlign: "right", color: "var(--muted)", fontSize: 13 }}>
                    <div>Saved: ${a.allocatedSaved.toFixed(2)}</div>
                    <div>{percent.toFixed(1)}%</div>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button className="btn" onClick={() => moveUp(i)}>↑</button>
                    <button className="btn" onClick={() => moveDown(i)}>↓</button>
                    <button className="btn" onClick={() => removeGoal(a.id)}>Remove</button>
                  </div>
                </div>
              </div>

              <div className="progress-track" style={{ marginBottom: 8 }}>
                <div className="progress-fill" style={{ width: `${percent}%` }} />
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", color: "var(--muted)", fontSize: 13 }}>
                <div>
                  {months ? <span>~{months} month(s) to complete</span> : <span>{remaining === 0 ? "Complete" : "Monthly allocation pending"}</span>}
                </div>
                <div>Priority: {i + 1}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
