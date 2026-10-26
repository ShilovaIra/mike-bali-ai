import { useFavorites } from './favoriteStore'
import { PartnerList } from './PartnerList'

export function Favorites({
  onOpen,
  onBrowse,
}: {
  onOpen: (id: string) => void
  onBrowse: () => void
}) {
  const { items } = useFavorites()

  return (
    <div className="stack">
      <h1>Избранное</h1>
      {items.length === 0 ? (
        <div className="notice">
          <p>Пока пусто. Отметьте партнёра в рекомендациях.</p>
          <button type="button" className="button" onClick={onBrowse}>
            К рекомендациям
          </button>
        </div>
      ) : (
        <PartnerList items={items} onOpen={onOpen} />
      )}
    </div>
  )
}
