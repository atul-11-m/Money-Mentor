import { Link, Outlet } from "react-router-dom";
import "./App.css";

export default function Layout() {
  return (
    <div className="app-container">
      <header className="nav-bar">
        <div className="nav-left">
          <div className="logo">MoneyMentor</div>
          <nav className="nav-links">
            <Link to="/" className="nav-link">Dashboard</Link>
            <Link to="/insights" className="nav-link">AI & Budget</Link>
          </nav>
        </div>
        <div className="nav-right">
          <button className="btn btn-primary">Connect</button>
        </div>
      </header>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
