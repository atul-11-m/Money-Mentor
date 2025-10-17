import MonthlySpendingChart from "./components/MonthlySpendingChart";
import TopCategoriesPie from "./components/TopCategoriesPie";
import TotalSpendingCard from "./components/TotalSpendingCard";
import CategoryBarChart from "./components/CategoryBarChart";
import CategoryTimeline from "./components/CategoryTimeline";
import UploadCSV from "./components/UploadCSV";
import "./App.css";

function App() {
  return (
    <>
  <h1 className="app-title">Finance Dashboard</h1>
  <UploadCSV />

      <div className="dashboard">
        {/* Top row: 3 cards */}
        <div className="row">
          <div className="card">
            <h2 className="card-title">Monthly Spending</h2>
            <div className="card-body">
              <MonthlySpendingChart />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Top Categories</h2>
            <div className="card-body">
              <TopCategoriesPie />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Totals</h2>
            <div className="card-body">
              <TotalSpendingCard />
            </div>
          </div>
        </div>

        {/* Bottom row: 2 cards */}
        <div className="row">
          <div className="card">
            <h2 className="card-title">Spending per Category</h2>
            <div className="card-body">
              <CategoryBarChart />
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Spending Over Time by Category</h2>
            <div className="card-body">
              <CategoryTimeline />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
