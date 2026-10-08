import { useEffect, useState } from 'react'
import { PartnerTypeFormModal } from './PartnerTypeFormModal'
import { partnerTypesApi, type PartnerType } from './partnerTypesApi'

export function PartnerTypesPage() {
  const [types, setTypes] = useState<PartnerType[]>([])
  const [error, setError] = useState<string | null>(null)
  const [modal, setModal] = useState<{ mode: 'create' | 'edit'; slug?: string } | null>(null)

  async function reload() {
    setTypes(await partnerTypesApi.list())
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
        <h1>Типы партнёров</h1>
        <button type="button" onClick={() => setModal({ mode: 'create' })} className="btn-primary">
          Добавить тип
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
              <th>Slug</th>
              <th>Тема</th>
              <th>Порядок</th>
              <th>В меню</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {types.map((type) => (
              <tr key={type.slug}>
                <td className="cell-quiet">{type.slug}</td>
                <td>{type.topic_label}</td>
                <td>{type.sort_order}</td>
                <td>
                  <span className={type.is_menu_visible ? 'state-on' : 'quiet'}>
                    {type.is_menu_visible ? 'да' : 'нет'}
                  </span>
                </td>
                <td>
                  <button
                    type="button"
                    className="btn-text"
                    onClick={() => setModal({ mode: 'edit', slug: type.slug })}
                  >
                    Изменить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal ? (
        <PartnerTypeFormModal
          mode={modal.mode}
          slug={modal.slug}
          onClose={() => setModal(null)}
          onSaved={async () => {
            setModal(null)
            await reload()
          }}
        />
      ) : null}
    </main>
  )
}
