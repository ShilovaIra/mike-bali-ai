import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { forgetFavorite, isSignedIn, listFavorites, saveFavorite, type Partner } from './api'

type FavoritesContextValue = {
  signed: boolean
  items: Partner[]
  has: (id: string) => boolean
  toggle: (id: string) => void
}

const FavoritesContext = createContext<FavoritesContextValue | null>(null)

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const signed = isSignedIn()
  const [items, setItems] = useState<Partner[]>([])

  useEffect(() => {
    if (!signed) return
    let cancelled = false
    listFavorites()
      .then((partners) => {
        if (!cancelled) setItems(partners)
      })
      .catch(() => {
        if (!cancelled) setItems([])
      })
    return () => {
      cancelled = true
    }
  }, [signed])

  function has(id: string) {
    return items.some((partner) => partner.id === id)
  }

  function toggle(id: string) {
    if (!signed) return
    const request = has(id) ? forgetFavorite(id) : saveFavorite(id)
    request
      .then(() => listFavorites())
      .then(setItems)
      .catch(() => setItems(items))
  }

  return (
    <FavoritesContext.Provider value={{ signed, items, has, toggle }}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavorites(): FavoritesContextValue {
  const value = useContext(FavoritesContext)
  if (!value) throw new Error('useFavorites must be used inside FavoritesProvider')
  return value
}
