import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'
import type { Partner } from './api'
import { FavoritesProvider } from './favoriteStore'
import { Home } from './Home'

afterEach(cleanup)

function partner(id: string, name: string): Partner {
  return {
    id,
    name,
    type: 'Обмен',
    blurb: 'На Бали',
    logo: '/partners/ex24pro_logo.png',
    action: 'Открыть',
  }
}

function renderHome(items: Partner[], view: 'hero' | 'list' = 'hero') {
  const onShowAll = vi.fn()
  const onBack = vi.fn()
  const onOpen = vi.fn()
  const onAsk = vi.fn()
  render(
    <FavoritesProvider>
      <Home
        partners={items}
        view={view}
        onShowAll={onShowAll}
        onBack={onBack}
        onOpen={onOpen}
        onAsk={onAsk}
      />
    </FavoritesProvider>,
  )
  return { onShowAll, onBack, onOpen, onAsk }
}

test('two partners stay in a static pair', () => {
  renderHome([partner('1', 'Early FX'), partner('2', 'Late FX')])

  const row = screen.getByRole('button', { name: /Early FX/ }).closest('.tiles')
  expect(row?.classList.contains('tiles-scroll')).toBe(false)
  expect(screen.getByRole('button', { name: /Late FX/ })).toBeTruthy()
})

test('the home row lists every partner when more than two are available', () => {
  const items = [
    partner('1', 'Early FX'),
    partner('2', 'Late FX'),
    partner('3', 'Butler Support'),
    partner('4', 'Mike eSIM'),
  ]
  renderHome(items)

  const row = screen.getByRole('button', { name: /Early FX/ }).closest('.tiles')
  expect(row?.classList.contains('tiles-scroll')).toBe(true)
  for (const item of items) {
    expect(screen.getByRole('button', { name: new RegExp(item.name) })).toBeTruthy()
  }
  expect(row?.querySelectorAll('.tile')).toHaveLength(4)
})

test('see all still opens the full vertical list', async () => {
  const user = userEvent.setup()
  const items = [partner('1', 'Early FX'), partner('2', 'Late FX'), partner('3', 'Butler Support')]
  const { onShowAll } = renderHome(items)

  await user.click(screen.getByRole('button', { name: /Смотреть все/ }))
  expect(onShowAll).toHaveBeenCalledOnce()

  cleanup()
  renderHome(items, 'list')
  expect(screen.getByRole('heading', { name: 'Рекомендации' })).toBeTruthy()
  for (const item of items) {
    expect(screen.getByRole('button', { name: new RegExp(item.name) })).toBeTruthy()
  }
})
