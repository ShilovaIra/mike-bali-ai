import { useState } from 'react'

type Shape = 'pending' | 'round' | 'wide'

export function PartnerLogo({ src }: { src: string }) {
  const [shape, setShape] = useState<Shape>('pending')

  return (
    <img
      src={src}
      alt=""
      className={`partner-logo is-${shape}`}
      onLoad={(event) => {
        const image = event.currentTarget
        const ratio = image.naturalWidth / image.naturalHeight
        setShape(ratio > 0.82 && ratio < 1.18 ? 'round' : 'wide')
      }}
    />
  )
}
