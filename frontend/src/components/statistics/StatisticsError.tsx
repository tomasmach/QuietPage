interface StatisticsErrorProps {
  error: Error;
  onRetry: () => void;
}

export function StatisticsError({ error, onRetry }: StatisticsErrorProps) {
  return (
    <div className="border-2 border-border bg-bg-panel p-12 text-center shadow-hard rounded-none">
      <p className="text-text-main font-mono text-lg mb-4">
        UNABLE TO LOAD STATISTICS
      </p>
      <p className="text-text-muted font-mono text-sm mb-6">
        {error.message}
      </p>
      <button
        onClick={onRetry}
        className="
          px-6 py-3 border-2 border-border bg-accent text-accent-fg rounded-none
          font-mono text-sm font-bold uppercase tracking-widest
          shadow-hard transition-all duration-150
          hover:translate-x-[2px] hover:translate-y-[2px]
        "
      >
        RETRY
      </button>
    </div>
  );
}
