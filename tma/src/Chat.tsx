import { useEffect, useId, useRef, useState, type FormEvent, type MouseEvent } from 'react'

type Message = {
  id: string
  from: 'mike' | 'user'
  text: string
}

const greeting: Message = {
  id: 'greeting',
  from: 'mike',
  text: 'Привет! Я Майк. Спрашивай что угодно о Бали.',
}

const trailingPunctuation = /[.,;:!?)]+$/

function openInTelegram(event: MouseEvent<HTMLAnchorElement>, url: string) {
  const openLink = window.Telegram?.WebApp?.openLink
  if (!openLink) return
  event.preventDefault()
  openLink(url, { try_instant_view: false })
}

function MessageText({ text }: { text: string }) {
  const parts = text.split(/(https?:\/\/[^\s]+)/g)
  return parts.map((part, index) => {
    if (!/^https?:\/\//.test(part)) return <span key={index}>{part}</span>
    const url = part.replace(trailingPunctuation, '')
    const trailing = part.slice(url.length)
    return (
      <span key={index}>
        <a href={url} target="_blank" rel="noreferrer" onClick={(event) => openInTelegram(event, url)}>
          {url}
        </a>
        {trailing}
      </span>
    )
  })
}

export function Chat({
  messages,
  replying,
  onSend,
}: {
  messages: Message[]
  replying: boolean
  onSend: (text: string) => void
}) {
  const [draft, setDraft] = useState('')
  const listRef = useRef<HTMLDivElement>(null)
  const inputId = useId()

  useEffect(() => {
    const list = listRef.current
    if (!list) return
    list.scrollTop = list.scrollHeight
  }, [messages, replying])

  function submit(event: FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || replying) return
    setDraft('')
    onSend(text)
  }

  return (
    <div className="chat">
      <div className="thread" ref={listRef}>
        <p className="sr-only" aria-live="polite">
          {replying
            ? 'Майк печатает'
            : messages.length > 1 && messages.at(-1)?.from === 'mike'
              ? messages.at(-1)?.text
              : ''}
        </p>
        {messages.map((message) => (
          <p key={message.id} className={message.from === 'mike' ? 'bubble-mike' : 'bubble-user'}>
            <MessageText text={message.text} />
          </p>
        ))}
        {replying ? (
          <p className="bubble-mike is-typing">
            <span className="dots" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            Майк печатает
          </p>
        ) : null}
      </div>
      <form className="composer" onSubmit={submit}>
        <label className="sr-only" htmlFor={inputId}>
          Сообщение
        </label>
        <input
          id={inputId}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Напишите Майку"
          autoComplete="off"
          enterKeyHint="send"
        />
        <button type="submit" className="button" disabled={draft.trim().length === 0 || replying}>
          Отправить
        </button>
      </form>
    </div>
  )
}

export { greeting }
export type { Message }
