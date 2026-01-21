import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { captureUtmParams } from './hooks/useUtmTracking'

// Capture UTM params from URL on app load (for marketing tracking)
captureUtmParams()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
