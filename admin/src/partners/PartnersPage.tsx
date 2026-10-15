import { useEffect, useState } from 'react'
import { apiFetch } from '../auth/authApi'
import { PartnerTypeFormModal } from '../partner-types/PartnerTypeFormModal'
import { partnerTypesApi, type PartnerType } from '../partner-types/partnerTypesApi'
import { PartnerFormModal } from './PartnerFormModal'
import { partnersApi, type Partner } from './partnersApi'

export function PartnersPage() {
  const [partners, setPartners] = useState<Partner[]>([])
  const [types, setTypes] = useState<PartnerType[]>([])
  const [error, setError] = useState<string | null>(null)
  const [ready, setReady] = useState(false)
  const [partnerModal, setPartnerModal] = useState<{
    mode: 'create' | 'edit'
    partnerId?: string
  } | null>(null)
  const [typeModal, setTypeModal] = useState<{
    mode: 'create' | 'edit'
    slug?: string
  } | null>(null)

  async function reload() {
    const [partnerItems, typeItems] = await Promise.all([
      partnersApi.list(),
      partnerTypesApi.list(),
    ])
    setPartners(partnerItems)
    setTypes(typeItems)
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

  const typeLabel = Object.fromEntries(types.map((t) => [t.slug, t.topic_label]))

  return (
    <main className="page partners-board">
      <section className="partners-main" aria-labelledby="partners-heading">
        <div className="page-head">
          <h1 id="partners-heading">Партнёры</h1>
          <button
            type="button"
            onClick={() => setPartnerModal({ mode: 'create' })}
            className="btn-primary"
          >
            Добавить партнёра
          </button>
        </div>
        {error ? (
          <p className="alert" role="alert">
            {error}
          </p>
        ) : null}
        {ready && partners.length === 0 ? (
          <p className="quiet">Пока нет партнёров.</p>
        ) : (
          <ul className="partner-cards">
            {partners.map((partner) => (
              <li key={partner.id} className="partner-card">
                <button
                  type="button"
                  className="partner-pen"
                  aria-label={`Изменить ${partner.name}`}
                  onClick={() => setPartnerModal({ mode: 'edit', partnerId: partner.id })}
                >
                  <PenIcon />
                </button>
                <PartnerLogo partnerId={partner.id} />
                <h2 className="partner-name">{partner.name}</h2>
                <dl className="partner-meta">
                  <div>
                    <dt>Тип</dt>
                    <dd>{typeLabel[partner.type] ?? 'Без названия'}</dd>
                  </div>
                  <div>
                    <dt>Порядок</dt>
                    <dd>{partner.sort_order}</dd>
                  </div>
                  <div>
                    <dt>Активен</dt>
                    <dd>{partner.is_active ? 'да' : 'нет'}</dd>
                  </div>
                </dl>
              </li>
            ))}
          </ul>
        )}
      </section>

      <aside className="partner-types-col" aria-labelledby="partner-types-heading">
        <div className="page-head partner-types-head">
          <h2 id="partner-types-heading">Типы партнёров</h2>
          <button
            type="button"
            onClick={() => setTypeModal({ mode: 'create' })}
            className="btn-primary"
          >
            Новый тип
          </button>
        </div>
        {ready && types.length === 0 ? (
          <p className="quiet">Пока нет типов.</p>
        ) : (
          <ul className="type-list">
            {types.map((type) => (
              <li key={type.slug} className="type-row">
                <span className="type-name">{type.topic_label}</span>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setTypeModal({ mode: 'edit', slug: type.slug })}
                >
                  Изменить
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      {partnerModal ? (
        <PartnerFormModal
          mode={partnerModal.mode}
          partnerId={partnerModal.partnerId}
          types={types}
          onClose={() => setPartnerModal(null)}
          onSaved={async () => {
            setPartnerModal(null)
            await reload()
          }}
        />
      ) : null}
      {typeModal ? (
        <PartnerTypeFormModal
          mode={typeModal.mode}
          slug={typeModal.slug}
          onClose={() => setTypeModal(null)}
          onSaved={async () => {
            setTypeModal(null)
            await reload()
          }}
        />
      ) : null}
    </main>
  )
}

function PartnerLogo({ partnerId }: { partnerId: string }) {
  const [src, setSrc] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    let objectUrl = ''
    apiFetch(`/api/partners/${encodeURIComponent(partnerId)}/logo`)
      .then((response) => (response.ok ? response.blob() : null))
      .then((blob) => {
        if (!blob || cancelled) return
        objectUrl = URL.createObjectURL(blob)
        setSrc(objectUrl)
      })
      .catch(() => {
        setSrc(null)
      })
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [partnerId])

  return (
    <span className="partner-logo-slot">
      {src ? <img src={src} alt="" /> : null}
    </span>
  )
}

function PenIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
      <path
        d="M11.1 1.7a1.4 1.4 0 0 1 2 2L5.2 11.6 2.4 12.4l.8-2.8 7.9-7.9Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path d="M9.6 3.2 12.4 6" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  )
}
