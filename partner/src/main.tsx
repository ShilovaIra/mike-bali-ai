import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from './theme.tsx'

function Stage() {
  return (
    <>
      <div className="scene scene-day" aria-hidden="true" />
      <div className="scene scene-dusk" aria-hidden="true" />
      <div className="veil" aria-hidden="true" />
    </>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Stage />
    <div className="cabinet">
      <ThemeProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ThemeProvider>
    </div>
  </StrictMode>,
)
