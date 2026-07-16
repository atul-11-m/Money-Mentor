import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="min-h-screen bg-ink p-6 text-white">
      <header className="mb-4 flex items-center justify-between rounded-lg border border-white/5 bg-gradient-to-r from-slate-800/95 to-slate-900/90 px-4 py-3">
        <div className="flex items-center gap-4">
          <div className="text-lg font-bold text-accent">MoneyMentor</div>
          <nav className="flex gap-3">
            <Link to="/" className="rounded-md px-2.5 py-1.5 text-white/85 transition hover:bg-white/5">
              Dashboard
            </Link>
            <Link to="/insights" className="rounded-md px-2.5 py-1.5 text-white/85 transition hover:bg-white/5">
              AI &amp; Budget
            </Link>
          </nav>
        </div>
        <button className="btn btn-primary">Connect</button>
      </header>

      <main className="mt-2">
        <Outlet />
      </main>
    </div>
  );
}
