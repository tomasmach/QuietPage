export function StatisticsLoading() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Summary Cards Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="theme-aware border-2 border-border bg-bg-panel p-6 h-32 rounded-none"
          />
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="theme-aware border-2 border-border bg-bg-panel p-6 h-80 rounded-none" />
        <div className="theme-aware border-2 border-border bg-bg-panel p-6 h-80 rounded-none" />
      </div>
    </div>
  );
}
