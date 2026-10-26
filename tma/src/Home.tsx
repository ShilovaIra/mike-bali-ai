import { IconBack } from './icons'
import type { Partner } from './api'
import { PartnerList } from './PartnerList'
import { SaveButton } from './SaveButton'

export function Home({
  partners,
  view,
  onShowAll,
  onBack,
  onOpen,
  onAsk,
}: {
  partners: Partner[]
  view: 'hero' | 'list'
  onShowAll: () => void
  onBack: () => void
  onOpen: (id: string) => void
  onAsk: () => void
}) {
  const homePartners = partners.slice(0, 2)
  if (view === 'list') {
    return (
      <div className="stack">
        <button type="button" className="back-link" onClick={onBack}>
          <IconBack />
          На главную
        </button>
        <h1>Рекомендации</h1>
        <PartnerList items={partners} onOpen={onOpen} />
        <button type="button" className="button" onClick={onAsk}>
          Спросите Майка о Бали
        </button>
      </div>
    )
  }

  return (
    <div className="stack">
      <article className="hero">
        <img
          src="/mike.jpg"
          alt="Майк у храмовых ворот на рисовых террасах Бали"
          width={1024}
          height={1024}
        />
        <div className="hero-scrim" />
        <div className="hero-copy">
          <h1>Майк</h1>
          <p>Ваш гид по Бали</p>
        </div>
        <p className="bubble">Привет! Я Майк. Спрашивай что угодно о Бали.</p>
      </article>

      <div className="section-head">
        <h2>Рекомендации для вас</h2>
        <button type="button" className="text-link" onClick={onShowAll}>
          Смотреть все
        </button>
      </div>

      {homePartners.length === 0 ? (
        <p className="empty-copy">Пока нет рекомендаций. Спросите Майка.</p>
      ) : (
        <div className="tiles">
          {homePartners.map((partner) => (
            <article key={partner.id} className="tile">
              <button type="button" className="tile-open" onClick={() => onOpen(partner.id)}>
                <img src={partner.logo} alt="" width={120} height={80} />
                <span className="tile-name">{partner.name}</span>
                <span className="tile-type">{partner.type}</span>
              </button>
              <SaveButton id={partner.id} name={partner.name} />
            </article>
          ))}
        </div>
      )}

      <button type="button" className="button" onClick={onAsk}>
        Спросите Майка о Бали
      </button>
    </div>
  )
}
