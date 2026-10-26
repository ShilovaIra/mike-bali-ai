import { useEffect, useState, type ReactNode } from 'react'
import { closedCopy, isSignedIn, listPartners, loadProfile, loadThread, sendMessage, type Partner } from './api'
import { Chat, greeting, type Message } from './Chat'
import { Favorites } from './SavedScreen'
import { useFavorites } from './favoriteStore'
import { Home } from './Home'
import { IconChat, IconClose, IconHeart, IconHome, IconMap, IconUser } from './icons'
import { MapSoon } from './MapSoon'
import { PartnerSheet } from './PartnerSheet'
import { Profile } from './Profile'
import { ThemeSwitch } from './ThemeSwitch'

type Tab = 'home' | 'map' | 'chat' | 'favorites' | 'profile'

export function App() {
  const signed = isSignedIn()
  const { items: saved } = useFavorites()
  const [tab, setTab] = useState<Tab>('home')
  const [homeView, setHomeView] = useState<'hero' | 'list'>('hero')
  const [openId, setOpenId] = useState<string | null>(null)
  const [partners, setPartners] = useState<Partner[]>([])
  const [partnersStatus, setPartnersStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [messages, setMessages] = useState<Message[]>([])
  const [replying, setReplying] = useState(false)
  const [profileName, setProfileName] = useState('')
  const catalog = [...partners, ...saved]
  const openPartner = openId ? catalog.find((partner) => partner.id === openId) : undefined

  useEffect(() => {
    let cancelled = false
    listPartners()
      .then((items) => {
        if (cancelled) return
        setPartners(items)
        setPartnersStatus('ready')
      })
      .catch(() => {
        if (!cancelled) setPartnersStatus('error')
      })
    if (!signed) return () => {
      cancelled = true
    }
    loadThread()
      .then((thread) => {
        if (cancelled) return
        setMessages(thread.length > 0 ? thread : [greeting])
      })
      .catch(() => {
        if (!cancelled) setMessages([greeting])
      })
    loadProfile()
      .then((profile) => {
        if (cancelled) return
        const name = [profile.firstName, profile.lastName].filter(Boolean).join(' ')
        setProfileName(name)
      })
      .catch(() => {
        if (!cancelled) setProfileName('')
      })
    return () => {
      cancelled = true
    }
  }, [signed])

  function selectTab(next: Tab) {
    setTab(next)
    if (next !== 'home') setHomeView('hero')
  }

  function ask() {
    selectTab('chat')
  }

  function send(text: string) {
    const userMessage: Message = { id: crypto.randomUUID(), from: 'user', text }
    setMessages((current) => [...current, userMessage])
    setReplying(true)
    sendMessage(text)
      .then((reply) => {
        setMessages((current) => [
          ...current,
          { id: crypto.randomUUID(), from: 'mike', text: reply },
        ])
      })
      .catch(() => {
        setMessages((current) => [
          ...current,
          { id: crypto.randomUUID(), from: 'mike', text: 'Майк не смог ответить. Попробуйте ещё раз.' },
        ])
      })
      .finally(() => setReplying(false))
  }

  const open = openPartner ? (
    <PartnerSheet key={openPartner.id} partner={openPartner} onClose={() => setOpenId(null)} />
  ) : null

  return (
    <div className="stage">
      <div className="app">
        <header className="header">
          <span className="icon-button is-quiet" aria-hidden="true">
            <IconClose />
          </span>
          <div className="brand">
            <img src="/mike.jpg" alt="" width={36} height={36} />
            <p className="brand-name">Mike Bali AI</p>
          </div>
          <ThemeSwitch />
        </header>

        <main className={tab === 'chat' ? 'main main-chat' : 'main'}>
          {tab === 'home' ? (
            partnersStatus === 'error' ? (
              <div className="stack">
                <p>Не удалось загрузить рекомендации</p>
              </div>
            ) : partnersStatus === 'loading' ? (
              <div className="stack">
                <p>Загрузка</p>
              </div>
            ) : (
              <Home
                partners={partners}
                view={homeView}
                onShowAll={() => setHomeView('list')}
                onBack={() => setHomeView('hero')}
                onOpen={setOpenId}
                onAsk={ask}
              />
            )
          ) : null}
          {tab === 'map' ? <MapSoon onAsk={ask} /> : null}
          {tab === 'chat' ? (
            signed ? (
              <Chat messages={messages} replying={replying} onSend={send} />
            ) : (
              <Closed title="Чат" />
            )
          ) : null}
          {tab === 'favorites' ? (
            signed ? (
              <Favorites
                onOpen={setOpenId}
                onBrowse={() => {
                  setHomeView('hero')
                  setTab('home')
                }}
              />
            ) : (
              <Closed title="Избранное" />
            )
          ) : null}
          {tab === 'profile' ? <Profile signed={signed} name={profileName} /> : null}
        </main>

        <nav className="tabs" aria-label="Разделы">
          <TabButton id="home" label="Главная" current={tab} onSelect={selectTab}>
            <IconHome active={tab === 'home'} />
          </TabButton>
          <TabButton id="map" label="Карта" soon current={tab} onSelect={selectTab}>
            <IconMap active={tab === 'map'} />
          </TabButton>
          <TabButton id="chat" label="Чат" current={tab} onSelect={selectTab}>
            <IconChat active={tab === 'chat'} />
          </TabButton>
          <TabButton id="favorites" label="Избранное" current={tab} onSelect={selectTab}>
            <IconHeart active={tab === 'favorites'} />
          </TabButton>
          <TabButton id="profile" label="Профиль" current={tab} onSelect={selectTab}>
            <IconUser active={tab === 'profile'} />
          </TabButton>
        </nav>
        {open}
      </div>
    </div>
  )
}

function Closed({ title }: { title: string }) {
  return (
    <div className="stack">
      <h1>{title}</h1>
      <p>{closedCopy}</p>
    </div>
  )
}

function TabButton({
  id,
  label,
  soon,
  current,
  onSelect,
  children,
}: {
  id: Tab
  label: string
  soon?: boolean
  current: Tab
  onSelect: (tab: Tab) => void
  children: ReactNode
}) {
  const active = current === id
  return (
    <button
      type="button"
      className={active ? 'tab is-active' : 'tab'}
      aria-current={active ? 'page' : undefined}
      aria-label={soon ? `${label}, скоро` : undefined}
      onClick={() => onSelect(id)}
    >
      <span className="tab-icon">
        {children}
        {soon ? <span className="soon">скоро</span> : null}
      </span>
      <span className="tab-label">{label}</span>
    </button>
  )
}
