import MonthlySpendingChart from "./components/MonthlySpendingChart";
import TopCategoriesPie from "./components/TopCategoriesPie";
import BudgetProgress from "./components/BudgetProgress";
import ChatbotPanel from "./components/ChatbotPanel";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <h1 className="app-title">Finance Dashboard</h1>

      <div className="dashboard">
        {/* Top row: 2 boxes */}
        <div className="row">
          <div className="card">
            <h2 className="card-title">Monthly Spending</h2>
            <div className="card-body">
              {/* Chart component */}
              <MonthlySpendingChart />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Top Categories</h2>
            <div className="card-body">
              {/* Pie chart */}
              <TopCategoriesPie />
            </div>
          </div>
        </div>

        {/* Bottom row: 3 boxes */}
        <div className="row">
          <div className="card">
            <h2 className="card-title">Savings Tips</h2>
            <ul className="card-list">
              <li>Cut subscriptions</li>
              <li>Cook at home</li>
              <li>Track impulse buys</li>
            </ul>
          </div>

          <div className="card">
            <h2 className="card-title">Budget Progress</h2>
            <div className="card-body">
              {/* Progress bar */}
              <BudgetProgress />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Chatbot Insights</h2>
            <div className="card-body card-chat">
              {/* Chat UI */}
              <ChatbotPanel />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


export default App;
