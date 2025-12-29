import { BookOpen } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-bg-app flex items-center justify-center p-4">
      <div className="panel shadow-hard p-8 max-w-md w-full">
        <div className="flex items-center justify-center mb-6">
          <BookOpen className="w-12 h-12 text-accent" />
        </div>
        <h1 className="text-2xl font-bold text-center mb-2">QuietPage</h1>
        <p className="text-text-muted text-center mb-6">
          Minimalist journaling and mental wellbeing tracking
        </p>
        <div className="space-y-4">
          <button className="btn-primary w-full">
            Get Started
          </button>
          <button className="btn-secondary w-full">
            Learn More
          </button>
        </div>
        <p className="text-text-muted text-sm text-center mt-6">
          React + TypeScript + Tailwind CSS + Vite
        </p>
      </div>
    </div>
  )
}

export default App
