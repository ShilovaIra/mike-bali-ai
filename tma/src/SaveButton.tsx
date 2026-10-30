import { IconHeart } from './icons'
import { useFavorites } from './favoriteStore'

export function SaveButton({ id, name }: { id: string; name: string }) {
  const { signed, has, toggle } = useFavorites()
  if (!signed) return null
  const saved = has(id)

  return (
    <button
      type="button"
      className={saved ? 'icon-button is-saved' : 'icon-button'}
      aria-pressed={saved}
      aria-label={saved ? `Убрать ${name} из избранного` : `Сохранить ${name}`}
      onClick={() => toggle(id)}
    >
      <IconHeart active={saved} />
    </button>
  )
}
