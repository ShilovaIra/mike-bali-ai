import { useEffect, useState, type FormEvent } from 'react'
import { partnerTypesApi, type PartnerType } from '../partner-types/partnerTypesApi'
import { partnersApi, type Partner } from '../partners/partnersApi'
import { knowledgeBaseApi, type KnowledgeBaseEntry } from './knowledgeBaseApi'

type Choice = { value: string; label: string }

function addableChoices(
  entries: KnowledgeBaseEntry[],
  partners: Partner[],
  types: PartnerType[],
): Choice[] {
  const partnerIds = new Set(entries.map((entry) => entry.partner_id))
  const typeLabel = Object.fromEntries(types.map((type) => [type.slug, type.topic_label]))
  return partners
    .filter((partner) => !partnerIds.has(partner.id))
    .map((partner) => ({
      value: partner.id,
      label: `${partner.name} (${typeLabel[partner.type] ?? partner.type})`,
    }))
}

export function KnowledgeBasePage() {
  const [entries, setEntries] = useState<KnowledgeBaseEntry[]>([])
  const [choices, setChoices] = useState<Choice[]>([])
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [ready, setReady] = useState(false)

  async function reload() {
    const [nextEntries, partners, types] = await Promise.all([
      knowledgeBaseApi.list(),
      partnersApi.list(),
      partnerTypesApi.list(),
    ])
    setEntries(nextEntries)
    setChoices(addableChoices(nextEntries, partners, types))
    setReady(true)
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
        <h1>База знаний</h1>
        {ready ? (
          <button type="button" onClick={() => setAdding(true)} className="btn-primary">
            Добавить запись
          </button>
        ) : null}
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
              <th>Имя</th>
              <th>Вид</th>
              <th>Ссылка</th>
              <th>В чате</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id}>
                <td>{entry.name}</td>
                <td>{entry.kind}</td>
                <td className="cell-quiet">{entry.referral_url}</td>
                <td>
                  <span className={entry.in_chat ? 'state-on' : 'quiet'}>
                    {entry.in_chat ? 'да' : 'нет'}
                  </span>
                </td>
                <td>
                  <button
                    type="button"
                    className="btn-danger"
                    onClick={async () => {
                      await knowledgeBaseApi.remove(entry.id)
                      await reload()
                    }}
                  >
                    Удалить запись
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {adding ? (
        <AddDialog
          choices={choices}
          onClose={() => setAdding(false)}
          onSaved={async () => {
            setAdding(false)
            await reload()
          }}
        />
      ) : null}
    </main>
  )
}

function AddDialog({
  choices,
  onClose,
  onSaved,
}: {
  choices: Choice[]
  onClose: () => void
  onSaved: () => Promise<void>
}) {
  const [value, setValue] = useState(choices[0]?.value ?? '')
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    try {
      await knowledgeBaseApi.add(value)
      await onSaved()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось добавить в базу знаний')
    }
  }

  return (
    <div className="scrim" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Добавить в базу знаний"
        className="dialog"
        onClick={(event) => event.stopPropagation()}
      >
        <h2>Добавить в базу знаний</h2>
        <form onSubmit={onSubmit} className="stack">
          {error ? (
            <p className="alert" role="alert">
              {error}
            </p>
          ) : null}
          <label className="field">
            Партнёр
            <select
              value={value}
              onChange={(event) => setValue(event.target.value)}
              className="control"
              required
            >
              {choices.map((choice) => (
                <option key={choice.value} value={choice.value}>
                  {choice.label}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="btn-primary">
            Сохранить запись
          </button>
        </form>
      </div>
    </div>
  )
}
