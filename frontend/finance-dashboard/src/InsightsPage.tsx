import BudgetProgress from "./components/BudgetProgress";
import AiChat from "./components/AiChat";

const cardClass = "flex flex-col rounded-xl border border-line bg-panel p-5 shadow-lg shadow-black/30";
const titleClass = "mb-3 text-lg font-semibold text-white";

function InsightsPage() {
  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">AI Insights &amp; Budget</h1>
      <p className="mb-4 text-muted">
        Upload a CSV to analyze with the AI or start a chat using existing data.
      </p>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className={cardClass}>
          <h2 className={titleClass}>Budget Progress</h2>
          <div className="w-full flex-1">
            <BudgetProgress />
          </div>
        </div>

        <div className={cardClass}>
          <h2 className={titleClass}>AI Insights</h2>
          <div className="flex h-[520px] w-full flex-col">
            <AiChat />
          </div>
        </div>
      </div>
    </div>
  );
}

export default InsightsPage;
