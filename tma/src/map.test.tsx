import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test } from 'vitest'
import { App } from './App'
import { FavoritesProvider } from './favoriteStore'
import { ThemeProvider } from './theme'

afterEach(() => {
  cleanup()
})

function renderApp() {
  document.documentElement.dataset.theme = 'light'
  return render(
    <ThemeProvider>
      <FavoritesProvider>
        <App />
      </FavoritesProvider>
    </ThemeProvider>,
  )
}

test('unsigned visitor sees the map placeholder', async () => {
  const user = userEvent.setup()
  renderApp()

  await user.click(screen.getByRole('button', { name: 'Карта, скоро' }))

  expect(screen.getByRole('heading', { name: 'Карта скоро' })).toBeTruthy()
  expect(screen.getByText('Места по-прежнему приходят ссылками в чате.')).toBeTruthy()
  expect(screen.getByRole('button', { name: 'Спросите Майка о Бали' })).toBeTruthy()
})

test('ask button opens the closed chat without sending a message', async () => {
  const user = userEvent.setup()
  const requests: string[] = []
  const originalFetch = globalThis.fetch
  globalThis.fetch = async (input) => {
    requests.push(String(input))
    return new Response('[]', { status: 200 })
  }

  try {
    renderApp()
    await user.click(screen.getByRole('button', { name: 'Карта, скоро' }))
    await user.click(screen.getByRole('button', { name: 'Спросите Майка о Бали' }))

    expect(screen.getByRole('heading', { name: 'Чат' })).toBeTruthy()
    expect(screen.getByText('Откройте Майка в Telegram.')).toBeTruthy()
    expect(screen.queryByRole('heading', { name: 'Карта скоро' })).toBeNull()
    expect(requests.some((url) => url.includes('/api/tma/messages'))).toBe(false)
  } finally {
    globalThis.fetch = originalFetch
  }
})
