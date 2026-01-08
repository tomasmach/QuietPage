import { useCallback, useState } from 'react';
import type { ReactNode } from 'react';
import { useFocusTrap, useOverlay } from '@/hooks/useFocusTrap';

interface AppLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  contextPanel?: ReactNode;
}

export function AppLayout({ children, sidebar, contextPanel }: AppLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isContextPanelOpen, setIsContextPanelOpen] = useState(false);

  const toggleSidebar = useCallback(() => setIsSidebarOpen(prev => !prev), []);
  const toggleContextPanel = useCallback(() => setIsContextPanelOpen(prev => !prev), []);
  const closeSidebar = useCallback(() => setIsSidebarOpen(false), []);
  const closeContextPanel = useCallback(() => setIsContextPanelOpen(false), []);

  useOverlay(isSidebarOpen, closeSidebar);
  useOverlay(isContextPanelOpen, closeContextPanel);

  const sidebarRef = useFocusTrap(isSidebarOpen);
  const contextPanelRef = useFocusTrap(isContextPanelOpen);

  return (
    <div className="min-h-screen bg-bg-app theme-aware">
      {/* Mobile Header with Hamburger Menu */}
      <div className="lg:hidden sticky top-0 z-30 bg-bg-app border-b-2 border-border px-4 py-3 flex items-center justify-between theme-aware">
        {sidebar && (
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-border/20 rounded-md transition-colors theme-aware"
            aria-label="Toggle sidebar"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}
        <div className="flex-1" />
        {contextPanel && (
          <button
            onClick={toggleContextPanel}
            className="p-2 hover:bg-border/20 rounded-md transition-colors theme-aware"
            aria-label="Toggle context panel"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        )}
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebar && isSidebarOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
            onClick={closeSidebar}
            aria-hidden="true"
          />
          <aside
            ref={sidebarRef as React.RefObject<HTMLElement>}
            className="lg:hidden fixed top-0 left-0 bottom-0 w-[280px] bg-bg-app z-50 overflow-y-auto border-r-2 border-border theme-aware"
            role="dialog"
            aria-modal="true"
            aria-label="Menu"
          >
            <div className="p-4 border-b-2 border-border flex justify-between items-center theme-aware">
              <h2 className="font-semibold">Menu</h2>
              <button
                onClick={closeSidebar}
                className="p-2 hover:bg-border/20 rounded-md transition-colors theme-aware"
                aria-label="Close sidebar"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {sidebar}
          </aside>
        </>
      )}

      {/* Mobile Context Panel Overlay */}
      {contextPanel && isContextPanelOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
            onClick={closeContextPanel}
            aria-hidden="true"
          />
          <aside
            ref={contextPanelRef as React.RefObject<HTMLElement>}
            className="lg:hidden fixed top-0 right-0 bottom-0 w-[320px] bg-bg-app z-50 overflow-y-auto border-l-2 border-border theme-aware"
            role="dialog"
            aria-modal="true"
            aria-label="Info"
          >
            <div className="p-4 border-b-2 border-border flex justify-between items-center theme-aware">
              <h2 className="font-semibold">Info</h2>
              <button
                onClick={closeContextPanel}
                className="p-2 hover:bg-border/20 rounded-md transition-colors theme-aware"
                aria-label="Close context panel"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {contextPanel}
          </aside>
        </>
      )}

      {/* Responsive Layout */}
      <div className="lg:grid lg:grid-cols-[minmax(240px,280px)_1fr_minmax(280px,320px)] lg:divide-x-2 divide-border min-h-screen">
        {/* Left Sidebar */}
        <aside className="hidden lg:block sticky top-0 h-screen overflow-y-auto bg-bg-app theme-aware">
          {sidebar}
        </aside>

        {/* Main Content */}
        <main className="min-h-screen overflow-y-auto bg-bg-app relative theme-aware">
          {children}
        </main>

        {/* Right Context Panel */}
        <aside className="hidden lg:block sticky top-0 h-screen overflow-y-auto bg-bg-app theme-aware">
          {contextPanel}
        </aside>
      </div>
    </div>
  );
}
