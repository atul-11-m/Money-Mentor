import BudgetProgress from "./components/BudgetProgress";
import ChatbotPanel from "./components/ChatbotPanel";
import "./App.css";

function InsightsPage() {
  return (
    <div>
      <h1 className="app-title">AI Insights & Budget</h1>

      <div className="dashboard">
        <div className="row">
          <div className="card">
            <h2 className="card-title">Budget Progress</h2>
            <div className="card-body">
              <BudgetProgress />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Chatbot Insights</h2>
            <div className="card-body card-chat">
              <ChatbotPanel />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InsightsPage;
