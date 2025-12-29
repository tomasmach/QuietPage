import React from 'react';
import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-6xl font-bold text-primary mb-6">QuietPage</h1>
        <p className="text-xl text-text mb-8">
          Minimalist journaling and mental wellbeing tracking
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/login"
            className="px-8 py-4 border-2 border-border bg-primary text-background font-medium
              shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]
              transition-all hover:-translate-y-0.5"
          >
            Log In
          </Link>
          <Link
            to="/signup"
            className="px-8 py-4 border-2 border-border bg-background text-primary font-medium
              shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]
              transition-all hover:-translate-y-0.5"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
}
