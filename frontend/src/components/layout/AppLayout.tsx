import type { ReactNode } from 'react';

interface AppLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  contextPanel?: ReactNode;
}

export function AppLayout({ children, sidebar, contextPanel }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <div className="grid grid-cols-[minmax(240px,280px)_1fr_minmax(280px,320px)] divide-x-2 divide-border min-h-screen">
        {/* Left Sidebar */}
        <aside className="sticky top-0 h-screen overflow-y-auto bg-background">
          {sidebar}
        </aside>

        {/* Main Content */}
        <main className="min-h-screen overflow-y-auto bg-background relative">
          {children}
        </main>

        {/* Right Context Panel */}
        <aside className="sticky top-0 h-screen overflow-y-auto bg-background">
          {contextPanel}
        </aside>
      </div>
    </div>
  );
}
