import type { Partner } from './api'
import { PartnerLogo } from './PartnerLogo'
import { SaveButton } from './SaveButton'

export function PartnerList({
  items,
  onOpen,
}: {
  items: Partner[]
  onOpen: (id: string) => void
}) {
  if (items.length === 0) {
    return <p className="empty-copy panel">Пока нет рекомендаций. Спросите Майка.</p>
  }

  return (
    <ul className="partner-list">
      {items.map((partner) => (
        <li key={partner.id} className="partner-row">
          <button type="button" className="row-open" onClick={() => onOpen(partner.id)}>
            <PartnerLogo src={partner.logo} />
            <span className="row-copy">
              <span className="row-name">{partner.name}</span>
              <span className="row-type">{partner.type}</span>
              <span className="row-blurb">{partner.blurb}</span>
            </span>
          </button>
          <SaveButton id={partner.id} name={partner.name} />
        </li>
      ))}
    </ul>
  )
}
