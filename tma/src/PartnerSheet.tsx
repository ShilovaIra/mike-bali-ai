import { useEffect, useRef, useState } from 'react'
import { openPartner, type Partner } from './api'
import { IconClose } from './icons'
import { PartnerLogo } from './PartnerLogo'
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

  const [href, setHref] = useState('')

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
    let cancelled = false
    openPartner(partner.id)
      .then((url) => {
        if (!cancelled) setHref(url)
      })
      .catch(() => {
        if (!cancelled) setHref('')
      })
    return () => {
      cancelled = true
    }
  }, [partner.id])

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
        <PartnerLogo src={partner.logo} />
        <p className="type-label">{partner.type}</p>
        <h2 id="sheet-title">{partner.name}</h2>
        <p className="sheet-blurb">{partner.blurb}</p>
        <a
          className="button"
          href={href || undefined}
          target={href ? '_blank' : undefined}
          rel={href ? 'noreferrer' : undefined}
          aria-disabled={href ? undefined : true}
          onClick={(event) => {
            if (!href) event.preventDefault()
          }}
        >
          {partner.action}
        </a>
      </div>
    </dialog>
  )
}
