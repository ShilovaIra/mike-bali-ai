import type { ReactNode } from 'react'
import { useTheme, type Theme } from './theme'

export function ThemeSwitch() {
  const { theme, choose } = useTheme()

  return (
    <div className="theme-toggle" role="group" aria-label="Тема">
      <ThemeOption theme="light" current={theme} onChoose={choose} label="Светлая тема">
        <IconSun />
      </ThemeOption>
      <ThemeOption theme="dark" current={theme} onChoose={choose} label="Тёмная тема">
        <IconMoon />
      </ThemeOption>
    </div>
  )
}

function ThemeOption({
  theme,
  current,
  onChoose,
  label,
  children,
}: {
  theme: Theme
  current: Theme
  onChoose: (next: Theme) => void
  label: string
  children: ReactNode
}) {
  const selected = current === theme

  return (
    <button
      type="button"
      aria-pressed={selected}
      aria-label={label}
      onClick={() => onChoose(theme)}
    >
      {children}
    </button>
  )
}

function IconSun() {
  return (
    <svg className="theme-icon" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="3.15" fill="none" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M12 3.2v2.1M12 18.7v2.1M3.2 12h2.1M18.7 12h2.1M5.8 5.8l1.5 1.5M16.7 16.7l1.5 1.5M18.2 5.8l-1.5 1.5M7.3 16.7l-1.5 1.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  )
}

function IconMoon() {
  return (
    <svg className="theme-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M15.2 3.6a7.4 7.4 0 1 0 5.2 10.6 5.8 5.8 0 0 1-5.2-10.6z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  )
}
