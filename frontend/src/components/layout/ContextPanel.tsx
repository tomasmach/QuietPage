import React, { ReactNode } from 'react';

interface ContextPanelProps {
  children?: ReactNode;
}

export function ContextPanel({ children }: ContextPanelProps) {
  return (
    <div className="p-6">
      {children}
    </div>
  );
}
