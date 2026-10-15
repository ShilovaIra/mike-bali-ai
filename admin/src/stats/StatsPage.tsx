import { useEffect, useState } from 'react'
import { buildDonutSlices } from './buildDonutSlices'
import { ShareDonut } from './ShareDonut'
import { statsApi, type BotStats } from './statsApi'
import { sourceLabel } from './sourceLabel'
import { stripLeadingEmoji } from './stripLeadingEmoji'

export function StatsPage() {
  const [stats, setStats] = useState<BotStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    statsApi
      .get()
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (error) {
    return (
      <main className="page">
        <div className="page-head">
          <h1>Статистика</h1>
        </div>
        <p className="alert" role="alert">
          {error}
        </p>
      </main>
    )
  }

  if (!stats) {
    return (
      <main className="page">
        <div className="page-head">
          <h1>Статистика</h1>
        </div>
        <p className="quiet">Загрузка…</p>
      </main>
    )
  }

  const topicSlices = buildDonutSlices(
    stats.topics_all_time.map((topic) => ({
      key: topic.slug,
      label: stripLeadingEmoji(topic.label),
      value: topic.unique_users,
    })),
  )
  const sourceSlices = buildDonutSlices(
    Object.entries(stats.users_by_first_source).map(([key, value]) => ({
      key,
      label: sourceLabel(key),
      value,
    })),
  )

  return (
    <main className="page">
      <div className="page-head">
        <h1>Статистика</h1>
      </div>

      <section className="metrics" aria-label="Ключевые показатели">
        <dl>
          <div>
            <dt>Всего пользователей</dt>
            <dd>{stats.total_users}</dd>
          </div>
          <div>
            <dt>Активны сегодня</dt>
            <dd>{stats.active_today}</dd>
          </div>
          <div>
            <dt>Новые сегодня</dt>
            <dd>{stats.new_users_today}</dd>
          </div>
          <div>
            <dt>Новые за 7 дней</dt>
            <dd>{stats.new_users_7d}</dd>
          </div>
          <div>
            <dt>Лиды (7 дней)</dt>
            <dd>{stats.leads_7d}</dd>
          </div>
          <div>
            <dt>Лиды (всего)</dt>
            <dd className="lead">{stats.leads_all_time}</dd>
          </div>
        </dl>
      </section>

      <section className="charts">
        <figure className="panel">
          <h2>Популярные темы</h2>
          <ShareDonut slices={topicSlices} />
        </figure>
        <figure className="panel">
          <h2>Источники пользователей</h2>
          <ShareDonut slices={sourceSlices} />
        </figure>
      </section>
    </main>
  )
}
