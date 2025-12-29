import React from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';

export function SettingsPage() {
  return (
    <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
      <div className="p-8">
        <h1 className="text-4xl font-bold text-primary mb-8">Settings</h1>
        <div className="border-2 border-border p-8 bg-background shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <p className="text-muted">Settings page coming soon...</p>
        </div>
      </div>
      <ThemeToggle />
    </AppLayout>
  );
}
