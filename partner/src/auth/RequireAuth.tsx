import { Navigate, Outlet, useNavigate } from 'react-router-dom'
import { Wordmark } from '../brand/Wordmark'
import { ThemeSwitch } from '../ThemeSwitch'
import { authApi } from './authApi'

export function RequireAuth() {
  const navigate = useNavigate()

  if (!authApi.getSession()) {
    return <Navigate to="/login" replace />
  }

  function logout() {
    authApi.logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="shell">
      <header className="topbar">
        <Wordmark />
        <div className="topbar-actions">
          <ThemeSwitch />
          <button type="button" onClick={logout} className="btn-secondary">
            Выйти
          </button>
        </div>
      </header>
      <Outlet />
    </div>
  )
}
