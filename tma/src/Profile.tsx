import { closedCopy } from './api'
import { IconUser } from './icons'
import { ThemeSwitch } from './ThemeSwitch'
import { useTheme } from './theme'

export function Profile({ signed, name }: { signed: boolean; name: string }) {
  const { theme } = useTheme()

  if (!signed) {
    return (
      <div className="stack">
        <h1>Профиль</h1>
        <p className="panel">{closedCopy}</p>
      </div>
    )
  }

  return (
    <div className="stack">
      <h1>Профиль</h1>
      <div className="user-identity">
        <span className="user-avatar" aria-hidden="true">
          <IconUser active />
        </span>
        <p className="user-name">{name}</p>
      </div>
      <p className="panel">Майк отвечает про пляжи, еду, дорогу и жильё. Спросите в чате.</p>
      <div className="theme-row">
        <div>
          <p className="theme-label">Тема</p>
          <p className="theme-value">{theme === 'dark' ? 'Тёмная' : 'Светлая'}</p>
        </div>
        <ThemeSwitch />
      </div>
    </div>
  )
}
