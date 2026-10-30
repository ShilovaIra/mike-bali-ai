import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Wordmark } from '../brand/Wordmark'
import { ThemeSwitch } from '../ThemeSwitch'
import { authApi } from './authApi'

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)

  if (authApi.getSession()) {
    return <Navigate to="/stats" replace />
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setPending(true)
    setError(null)
    const result = await authApi.login({ email, password })
    setPending(false)
    if (!result.ok) {
      setError(result.error)
      return
    }
    navigate('/stats', { replace: true })
  }

  return (
    <main className="login-stage">
      <div className="login">
        <div className="login-tools">
          <ThemeSwitch />
        </div>
        <Wordmark />
        <h1>Кабинет партнёра</h1>
        <form onSubmit={onSubmit} className="stack">
          <label className="field">
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="control"
              autoComplete="username"
              required
            />
          </label>
          <label className="field">
            Пароль
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="control"
              autoComplete="current-password"
              required
            />
          </label>
          {error ? (
            <p className="alert" role="alert">
              {error}
            </p>
          ) : null}
          <button type="submit" disabled={pending} className="btn-primary">
            Войти
          </button>
        </form>
      </div>
    </main>
  )
}
