import { useEffect, useState, type FormEvent } from 'react'
import { partnersApi, type Partner } from '../partners/partnersApi'
import { partnerUsersApi, type PartnerUserRow } from './partnerUsersApi'

export function PartnerUsersPage() {
  const [users, setUsers] = useState<PartnerUserRow[]>([])
  const [partners, setPartners] = useState<Partner[]>([])
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  async function reload() {
    const [userItems, partnerItems] = await Promise.all([
      partnerUsersApi.list(),
      partnersApi.list(),
    ])
    setUsers(userItems)
    setPartners(partnerItems)
  }

  useEffect(() => {
    let cancelled = false
    reload().catch((err: Error) => {
      if (!cancelled) setError(err.message)
    })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main className="page">
      <div className="page-head">
        <h1>Пользователи партнёров</h1>
        <button type="button" onClick={() => setModalOpen(true)} className="btn-primary">
          Добавить пользователя
        </button>
      </div>
      {error ? (
        <p className="alert" role="alert">
          {error}
        </p>
      ) : null}
      <div className="sheet-wrap">
        <table className="sheet">
          <thead>
            <tr>
              <th>Email</th>
              <th>Партнёры</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map((row) => (
              <tr key={row.id}>
                <td>{row.email}</td>
                <td>{row.partners.map((p) => p.name).join(', ')}</td>
                <td>
                  <button
                    type="button"
                    className="btn-danger"
                    onClick={async () => {
                      await partnerUsersApi.remove(row.id)
                      await reload()
                    }}
                  >
                    Удалить пользователя
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {modalOpen ? (
        <CreatePartnerUserModal
          partners={partners}
          onClose={() => setModalOpen(false)}
          onSaved={async () => {
            setModalOpen(false)
            await reload()
          }}
        />
      ) : null}
    </main>
  )
}

function CreatePartnerUserModal({
  partners,
  onClose,
  onSaved,
}: {
  partners: Partner[]
  onClose: () => void
  onSaved: () => void
}) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [selected, setSelected] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (selected.length === 0) {
      setError('Выберите хотя бы одного партнёра')
      return
    }
    try {
      await partnerUsersApi.create({ email, password, partner_ids: selected })
      onSaved()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить')
    }
  }

  return (
    <div className="scrim" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Новый пользователь"
        className="dialog"
        onClick={(e) => e.stopPropagation()}
      >
        <h2>Новый пользователь</h2>
        <form onSubmit={onSubmit} className="stack">
          <label className="field">
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="control"
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
              required
            />
          </label>
          <fieldset>
            <legend className="field">Партнёры</legend>
            {partners.length === 0 ? (
              <p className="quiet">Нет партнёров. Сначала добавьте их в разделе «Партнёры».</p>
            ) : (
              <div className="checks">
                {partners.map((partner) => (
                  <label key={partner.id} className="check">
                    <input
                      type="checkbox"
                      checked={selected.includes(partner.id)}
                      onChange={(e) => {
                        setSelected((prev) =>
                          e.target.checked
                            ? [...prev, partner.id]
                            : prev.filter((id) => id !== partner.id),
                        )
                      }}
                    />
                    {partner.name}
                  </label>
                ))}
              </div>
            )}
          </fieldset>
          {error ? (
            <p className="alert" role="alert">
              {error}
            </p>
          ) : null}
          <div className="actions">
            <button type="submit" className="btn-primary">
              Сохранить пользователя
            </button>
            <button type="button" onClick={onClose} className="btn-secondary">
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
