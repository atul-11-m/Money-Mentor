import MonthlySpendingChart from "./components/MonthlySpendingChart";
import TopCategoriesPie from "./components/TopCategoriesPie";
import TotalSpendingCard from "./components/TotalSpendingCard";
import CategoryBarChart from "./components/CategoryBarChart";
import CategoryTimeline from "./components/CategoryTimeline";
import UploadCSV from "./components/UploadCSV";

const cardClass = "flex flex-col rounded-xl border border-line bg-panel p-5 shadow-lg shadow-black/30";
const titleClass = "mb-3 text-lg font-semibold text-white";
const bodyClass = "flex min-h-[260px] w-full flex-1 flex-col justify-center";

function App() {
  return (
    <>
      <h1 className="mb-6 text-3xl font-bold">Finance Dashboard</h1>
      <UploadCSV />

      <div className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className={cardClass}>
            <h2 className={titleClass}>Monthly Spending</h2>
            <div className={bodyClass}>
              <MonthlySpendingChart />
            </div>
          </div>

          <div className={cardClass}>
            <h2 className={titleClass}>Top Categories</h2>
            <div className={bodyClass}>
              <TopCategoriesPie />
            </div>
          </div>

          <div className={cardClass}>
            <h2 className={titleClass}>Totals</h2>
            <div className={bodyClass}>
              <TotalSpendingCard />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className={cardClass}>
            <h2 className={titleClass}>Spending per Category</h2>
            <div className={bodyClass}>
              <CategoryBarChart />
            </div>
          </div>

          <div className={cardClass}>
            <h2 className={titleClass}>Spending Over Time by Category</h2>
            <div className={bodyClass}>
              <CategoryTimeline />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
