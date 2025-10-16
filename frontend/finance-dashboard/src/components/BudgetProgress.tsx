export default function BudgetProgress() {
  const spent = 65; // percent
  return (
    <div className="w-full bg-gray-200 rounded-full h-4">
      <div
        className="bg-green-500 h-4 rounded-full"
        style={{ width: `${spent}%` }}
      />
    </div>
  );
}
