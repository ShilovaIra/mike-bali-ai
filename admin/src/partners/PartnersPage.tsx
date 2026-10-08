import { useEffect, useState } from 'react'
import { partnerTypesApi, type PartnerType } from '../partner-types/partnerTypesApi'
import { PartnerFormModal } from './PartnerFormModal'
import { partnersApi, type Partner } from './partnersApi'

export function PartnersPage() {
  const [partners, setPartners] = useState<Partner[]>([])
  const [types, setTypes] = useState<PartnerType[]>([])
  const [error, setError] = useState<string | null>(null)
  const [modal, setModal] = useState<{ mode: 'create' | 'edit'; partnerId?: string } | null>(
    null,
  )

  async function reload() {
    const [partnerItems, typeItems] = await Promise.all([
      partnersApi.list(),
      partnerTypesApi.list(),
    ])
    setPartners(partnerItems)
    setTypes(typeItems)
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

  const typeLabel = Object.fromEntries(types.map((t) => [t.slug, t.topic_label]))

  return (
    <main className="page">
      <div className="page-head">
        <h1>Партнёры</h1>
        <button type="button" onClick={() => setModal({ mode: 'create' })} className="btn-primary">
          Добавить партнёра
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
              <th>Файл логотипа</th>
              <th>Имя</th>
              <th>Тип</th>
              <th>Порядок</th>
              <th>Активен</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {partners.map((partner) => (
              <tr key={partner.id}>
                <td className="cell-quiet">{partner.logo_path}</td>
                <td>{partner.name}</td>
                <td>{typeLabel[partner.type] ?? 'Без названия'}</td>
                <td>{partner.sort_order}</td>
                <td>
                  <span className={partner.is_active ? 'state-on' : 'quiet'}>
                    {partner.is_active ? 'да' : 'нет'}
                  </span>
                </td>
                <td>
                  <button
                    type="button"
                    className="btn-text"
                    onClick={() => setModal({ mode: 'edit', partnerId: partner.id })}
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
        <PartnerFormModal
          mode={modal.mode}
          partnerId={modal.partnerId}
          types={types}
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
