import { useEffect, useState } from 'react'
import { buildDonutSlices } from './buildDonutSlices'
import { ShareDonut } from './ShareDonut'
import { partnerApi, type PartnerRef, type PartnerStats } from './statsApi'

export function StatsPage() {
  const [partners, setPartners] = useState<PartnerRef[] | null>(null)
  const [currentId, setCurrentId] = useState<string | null>(null)
  const [stats, setStats] = useState<PartnerStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    partnerApi
      .me()
      .then((me) => {
        if (cancelled) return
        setPartners(me.partners)
        setCurrentId(me.partners[0]?.id ?? null)
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!currentId) {
      setStats(null)
      return
    }
    let cancelled = false
    partnerApi
      .stats(currentId)
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [currentId])

  if (error) {
    return (
      <main className="page">
        <div className="page-stack">
          <h1>Статистика</h1>
          <p className="alert" role="alert">
            {error}
          </p>
        </div>
      </main>
    )
  }

  if (!partners) {
    return (
      <main className="page">
        <div className="page-stack">
          <h1>Статистика</h1>
          <p className="quiet">Загрузка…</p>
        </div>
      </main>
    )
  }

  const current = partners.find((p) => p.id === currentId)
  const slices = stats
    ? buildDonutSlices([
        {
          key: 'opened',
          label: 'Показы с переходом',
          value: stats.all_time.opened_views,
        },
        {
          key: 'not_opened',
          label: 'Показы без перехода',
          value: stats.all_time.views - stats.all_time.opened_views,
        },
      ])
    : []

  return (
    <main className="page">
      <div className="page-stack">
        <h1>Статистика</h1>
        {partners.length > 1 ? (
          <label className="field">
            Партнёр
            <select
              value={currentId ?? ''}
              onChange={(e) => setCurrentId(e.target.value)}
              className="control"
            >
              {partners.map((partner) => (
                <option key={partner.id} value={partner.id}>
                  {partner.name}
                </option>
              ))}
            </select>
          </label>
        ) : current ? (
          <p className="partner-name">{current.name}</p>
        ) : null}

        {!stats ? (
          <p className="quiet">Загрузка…</p>
        ) : (
          <div className="stats-layout">
            <div className="stat-groups">
              <section aria-label="Пользователи категории" className="stat-grid">
                <article className="stat-card">
                  <p>Пользователей, выбравших {stats.category_users.phrase} (всё время)</p>
                  <p className="stat-value">{stats.category_users.all_time}</p>
                </article>
                <article className="stat-card">
                  <p>Пользователей, выбравших {stats.category_users.phrase} (30 дней)</p>
                  <p className="stat-value">{stats.category_users.last_30_days}</p>
                </article>
              </section>
              <section aria-label="За всё время" className="stat-grid">
                <article className="stat-card">
                  <p>Показы (всё время)</p>
                  <p className="stat-value">{stats.all_time.views}</p>
                </article>
                <article className="stat-card">
                  <p>Переходы (всё время)</p>
                  <p className="stat-value">{stats.all_time.referral_clicks}</p>
                </article>
              </section>
              <section aria-label="За 30 дней" className="stat-grid">
                <article className="stat-card">
                  <p>Показы (30 дней)</p>
                  <p className="stat-value">{stats.last_30_days.views}</p>
                </article>
                <article className="stat-card">
                  <p>Переходы (30 дней)</p>
                  <p className="stat-value">{stats.last_30_days.referral_clicks}</p>
                </article>
              </section>
            </div>
            <section aria-label="Показы с переходом и без" className="panel stats-donut">
              <ShareDonut slices={slices} />
            </section>
          </div>
        )}
      </div>
    </main>
  )
}
