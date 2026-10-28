import type { ReactNode } from 'react'

type IconProps = {
  active?: boolean
}

function Svg({ children }: { children: ReactNode }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
      {children}
    </svg>
  )
}

const stroke = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.75,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}

export function IconForward() {
  return (
    <Svg>
      <path d="M9 5.5 15.5 12 9 18.5" {...stroke} />
    </Svg>
  )
}

export function IconBack() {
  return (
    <Svg>
      <path d="M14.5 5.5 8 12l6.5 6.5" {...stroke} />
    </Svg>
  )
}

export function IconClose() {
  return (
    <Svg>
      <path d="M6 6l12 12M18 6L6 18" {...stroke} />
    </Svg>
  )
}

export function IconHome({ active }: IconProps) {
  return (
    <Svg>
      <path
        d="M4 10.6 12 4l8 6.6V20a1 1 0 0 1-1 1h-5.2v-6.2H10.2V21H5a1 1 0 0 1-1-1z"
        {...stroke}
        fill={active ? 'currentColor' : 'none'}
      />
    </Svg>
  )
}

export function IconMap({ active }: IconProps) {
  return (
    <Svg>
      <path
        d="M12 21s6-5.2 6-10a6 6 0 1 0-12 0c0 4.8 6 10 6 10z"
        {...stroke}
        fill={active ? 'currentColor' : 'none'}
      />
      <circle cx="12" cy="11" r="1.6" fill="currentColor" stroke="none" />
    </Svg>
  )
}

export function IconChat({ active }: IconProps) {
  return (
    <Svg>
      <path
        d="M5 16.5 3.8 20.2 7.6 19A8.5 8.5 0 1 0 5 16.5z"
        {...stroke}
        fill={active ? 'currentColor' : 'none'}
      />
    </Svg>
  )
}

export function IconHeart({ active }: IconProps) {
  return (
    <Svg>
      <path
        d="M12 19.4 5.4 12.8a3.8 3.8 0 0 1 5.4-5.4L12 8.6l1.2-1.2a3.8 3.8 0 0 1 5.4 5.4z"
        {...stroke}
        fill={active ? 'currentColor' : 'none'}
      />
    </Svg>
  )
}

export function IconUser({ active }: IconProps) {
  return (
    <Svg>
      <circle cx="12" cy="8.2" r="3.1" {...stroke} fill={active ? 'currentColor' : 'none'} />
      <path d="M5.2 19.2a6.8 6.8 0 0 1 13.6 0" {...stroke} />
    </Svg>
  )
}
