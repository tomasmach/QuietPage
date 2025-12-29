import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';

export function DashboardPage() {
  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-primary border-b-2 border-border pb-2">
              Stats
            </h2>
            <p className="text-muted">Dashboard widgets coming soon...</p>
          </div>
        </ContextPanel>
      }
    >
      <div className="p-8">
        <h1 className="text-4xl font-bold text-primary mb-8">Dashboard</h1>
        <div className="border-2 border-border p-8 bg-background shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <p className="text-text">Welcome to QuietPage!</p>
          <p className="text-muted mt-2">Dashboard content coming soon...</p>
        </div>
      </div>
      <ThemeToggle />
    </AppLayout>
  );
}
