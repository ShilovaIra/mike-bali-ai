export type Partner = {
  id: string
  name: string
  type: string
  blurb: string
  logo: string
  action: string
}

type PartnerPayload = {
  id: string
  name: string
  blurb: string
  type_label: string
  action: string
  logo_url: string
}

export type ThreadMessage = {
  id: string
  from: 'mike' | 'user'
  text: string
}

type TelegramWebApp = {
  initData?: string
  close?: () => void
  openLink?: (url: string, options?: { try_instant_view?: boolean }) => void
}

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp }
  }
}

export const closedCopy = 'Откройте Майка в Telegram.'

const VISITOR_KEY = 'mike-bali-tma-visitor'
let rememberedVisitor = ''

export function visitorId(): string {
  if (rememberedVisitor) return rememberedVisitor
  try {
    const stored = localStorage.getItem(VISITOR_KEY)
    if (stored) {
      rememberedVisitor = stored
      return stored
    }
  } catch {
    /* private mode */
  }
  rememberedVisitor = crypto.randomUUID()
  try {
    localStorage.setItem(VISITOR_KEY, rememberedVisitor)
  } catch {
    /* private mode */
  }
  return rememberedVisitor
}

export function initData(): string {
  return window.Telegram?.WebApp?.initData ?? ''
}

export function isSignedIn(): boolean {
  return initData().length > 0
}

export function closeApp() {
  window.Telegram?.WebApp?.close?.()
}

function authHeaders(): HeadersInit {
  const data = initData()
  return data ? { Authorization: `tma ${data}` } : {}
}

function asPartner(payload: PartnerPayload): Partner {
  return {
    id: payload.id,
    name: payload.name,
    type: payload.type_label,
    blurb: payload.blurb,
    logo: payload.logo_url,
    action: payload.action,
  }
}

export async function listPartners(): Promise<Partner[]> {
  const response = await fetch('/api/tma/partners')
  if (!response.ok) throw new Error('Не удалось загрузить рекомендации')
  const payload: PartnerPayload[] = await response.json()
  return payload.map(asPartner)
}

export async function listFavorites(): Promise<Partner[]> {
  const response = await fetch('/api/tma/favorites', { headers: authHeaders() })
  if (!response.ok) throw new Error('Не удалось загрузить избранное')
  const payload: PartnerPayload[] = await response.json()
  return payload.map(asPartner)
}

export async function saveFavorite(id: string): Promise<void> {
  const response = await fetch(`/api/tma/favorites/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
  })
  if (!response.ok) throw new Error('Не удалось сохранить')
}

export async function forgetFavorite(id: string): Promise<void> {
  const response = await fetch(`/api/tma/favorites/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!response.ok) throw new Error('Не удалось убрать из избранного')
}

export async function openPartner(id: string): Promise<string> {
  const headers: Record<string, string> = {}
  const data = initData()
  if (data) headers.Authorization = `tma ${data}`
  else headers['X-Visitor-Id'] = visitorId()
  const response = await fetch(`/api/tma/partners/${id}/open`, {
    method: 'POST',
    headers,
  })
  if (!response.ok) throw new Error('Не удалось открыть партнёра')
  const payload: { url: string } = await response.json()
  return payload.url
}

export async function loadProfile(): Promise<{ firstName: string; lastName: string; photoUrl: string }> {
  const response = await fetch('/api/tma/me', { headers: authHeaders() })
  if (!response.ok) throw new Error('Не удалось загрузить профиль')
  const payload: { first_name: string; last_name: string; photo_url?: string } = await response.json()
  return {
    firstName: payload.first_name,
    lastName: payload.last_name,
    photoUrl: payload.photo_url ?? '',
  }
}

export async function loadThread(): Promise<ThreadMessage[]> {
  const response = await fetch('/api/tma/messages', { headers: authHeaders() })
  if (!response.ok) throw new Error('Не удалось загрузить чат')
  const payload: { role: string; content: string }[] = await response.json()
  return payload.map((message, index) => ({
    id: `${index}-${message.role}`,
    from: message.role === 'user' ? 'user' : 'mike',
    text: message.content,
  }))
}

export async function sendMessage(text: string): Promise<string> {
  const response = await fetch('/api/tma/messages', {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) throw new Error('Майк не смог ответить')
  const payload: { reply: string } = await response.json()
  return payload.reply
}
