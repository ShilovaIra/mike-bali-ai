import { IconForward, IconMap } from './icons'

export function MapSoon({ onAsk }: { onAsk: () => void }) {
  return (
    <div className="stack notice">
      <IconMap />
      <h1>Карта скоро</h1>
      <p>Места по-прежнему приходят ссылками в чате.</p>
      <button type="button" className="button button-ask" onClick={onAsk}>
        Спросите Майка о Бали
        <IconForward />
      </button>
    </div>
  )
}
