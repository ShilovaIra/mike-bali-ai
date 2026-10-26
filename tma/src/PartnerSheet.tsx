import { useEffect, useRef, useState } from 'react'
import { isSignedIn, openPartner, type Partner } from './api'
import { IconClose } from './icons'
import { SaveButton } from './SaveButton'

export function PartnerSheet({
  partner,
  onClose,
}: {
  partner: Partner
  onClose: () => void
}) {
  const ref = useRef<HTMLDialogElement>(null)
  const ignoreClose = useRef(false)

  const [href, setHref] = useState(partner.href)

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    dialog.showModal()
    return () => {
      ignoreClose.current = true
      if (dialog.open) dialog.close()
    }
  }, [])

  useEffect(() => {
    if (!isSignedIn()) return
    let cancelled = false
    openPartner(partner.id)
      .then((url) => {
        if (!cancelled) setHref(url)
      })
      .catch(() => {
        if (!cancelled) setHref(partner.href)
      })
    return () => {
      cancelled = true
    }
  }, [partner.id, partner.href])

  return (
    <dialog
      ref={ref}
      className="sheet"
      aria-labelledby="sheet-title"
      onClose={() => {
        if (!ignoreClose.current) onClose()
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="sheet-panel">
        <div className="sheet-bar">
          <button type="button" className="icon-button" onClick={onClose} aria-label="Закрыть">
            <IconClose />
          </button>
          <SaveButton id={partner.id} name={partner.name} />
        </div>
        <img className="sheet-logo" src={partner.logo} alt="" width={96} height={96} />
        <p className="type-label">{partner.type}</p>
        <h2 id="sheet-title">{partner.name}</h2>
        <p className="sheet-blurb">{partner.blurb}</p>
        <a className="button" href={href} target="_blank" rel="noreferrer">
          {partner.action}
        </a>
      </div>
    </dialog>
  )
}
