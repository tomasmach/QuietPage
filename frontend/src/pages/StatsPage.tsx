import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';

export function StatsPage() {
  return (
    <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
      <div className="p-8">
        <h1 className="text-4xl font-bold text-text-main mb-8">Statistics</h1>
        <div className="border-2 border-border p-8 bg-bg-panel shadow-hard">
          <p className="text-text-muted">Statistics page coming soon...</p>
        </div>
      </div>
      <ThemeToggle />
    </AppLayout>
  );
}
