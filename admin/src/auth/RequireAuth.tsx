import { useEffect, useState } from 'react'
import { NavLink, Navigate, Outlet, useNavigate } from 'react-router-dom'
import { Wordmark } from '../brand/Wordmark'
import { apiFetch, authApi, SESSION_EVENT } from './authApi'

const links = [
  { to: '/stats', label: 'Статистика' },
  { to: '/partners', label: 'Партнёры' },
  { to: '/knowledge-base', label: 'База знаний' },
  { to: '/partner-users', label: 'Пользователи партнёров' },
]

export function RequireAuth() {
  const navigate = useNavigate()
  const [session, setSession] = useState(() => authApi.getSession())

  useEffect(() => {
    const sync = () => setSession(authApi.getSession())
    window.addEventListener(SESSION_EVENT, sync)
    return () => window.removeEventListener(SESSION_EVENT, sync)
  }, [])

  useEffect(() => {
    if (!session) return
    void apiFetch('/api/auth/me')
  }, [session])

  if (!session) {
    return <Navigate to="/login" replace />
  }

  function logout() {
    authApi.logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="shell">
      <aside className="rail">
        <Wordmark />
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className="nav-link">
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <button type="button" onClick={logout} className="btn-secondary">
            Выйти
          </button>
        </header>
        <Outlet />
      </div>
    </div>
  )
}
