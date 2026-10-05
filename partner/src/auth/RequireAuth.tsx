import { Link, Navigate, Outlet, useNavigate } from 'react-router-dom'
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
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
        <Link to="/" className="text-sm font-medium tracking-wide text-slate-700">
          Mike Bali AI
        </Link>
        <button
          type="button"
          onClick={logout}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Выйти
        </button>
      </header>
      <Outlet />
    </div>
  )
}
