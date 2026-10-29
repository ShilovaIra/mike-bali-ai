import { IconBack, IconForward } from './icons'
import type { Partner } from './api'
import { PartnerList } from './PartnerList'
import { PartnerLogo } from './PartnerLogo'
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
  if (view === 'list') {
    return (
      <div className="stack">
        <button type="button" className="back-link" onClick={onBack}>
          <IconBack />
          На главную
        </button>
        <h1>Рекомендации</h1>
        <PartnerList items={partners} onOpen={onOpen} />
        <button type="button" className="button button-ask" onClick={onAsk}>
          Спросите Майка о Бали
          <IconForward />
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
          <IconForward />
        </button>
      </div>

      {partners.length === 0 ? (
        <p className="empty-copy panel">Пока нет рекомендаций. Спросите Майка.</p>
      ) : (
        <div className={partners.length > 2 ? 'tiles tiles-scroll' : 'tiles'}>
          {partners.map((partner) => (
            <article key={partner.id} className="tile">
              <button type="button" className="tile-open" onClick={() => onOpen(partner.id)}>
                <PartnerLogo src={partner.logo} />
                <span className="tile-name">{partner.name}</span>
                <span className="tile-type">{partner.type}</span>
              </button>
              <SaveButton id={partner.id} name={partner.name} />
            </article>
          ))}
        </div>
      )}

      <button type="button" className="button button-ask" onClick={onAsk}>
        Спросите Майка о Бали
        <IconForward />
      </button>
    </div>
  )
}
