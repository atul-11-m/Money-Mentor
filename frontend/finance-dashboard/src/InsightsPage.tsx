import BudgetProgress from "./components/BudgetProgress";
import ChatbotPanel from "./components/ChatbotPanel";
import "./App.css";
import AiChat from "./components/AiChat";

function InsightsPage() {
  return (
    <div>
      <h1 className="app-title">AI Insights & Budget</h1>

      <div style={{ marginBottom: 12 }}>
        <p style={{ color: "var(--muted)" }}>Upload a CSV to analyze with the AI or start a chat using existing data.</p>
      </div>

      <div className="dashboard">
        <div className="row">
          <div className="card">
            <h2 className="card-title">Budget Progress</h2>
            <div className="card-body">
              <BudgetProgress />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">AI Insights</h2>
            <div className="card-body card-chat" style={{ alignItems: "stretch" }}>
              <AiChat />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InsightsPage;
