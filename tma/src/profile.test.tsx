import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test } from 'vitest'
import { App } from './App'
import { FavoritesProvider } from './favoriteStore'
import { ThemeProvider } from './theme'

afterEach(() => {
  cleanup()
  delete window.Telegram
  document.documentElement.dataset.theme = 'light'
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

function signIn(profile: { first_name: string; last_name: string; photo_url: string }) {
  window.Telegram = { WebApp: { initData: 'signed' } }
  const originalFetch = globalThis.fetch
  globalThis.fetch = async (input) => {
    const url = String(input)
    if (url.includes('/api/tma/me')) return Response.json(profile)
    return Response.json([])
  }
  return () => {
    globalThis.fetch = originalFetch
  }
}

test('signed-in profile shows the telegram photo and name', async () => {
  const user = userEvent.setup()
  const photo = 'https://t.me/i/userpic/320/anna.jpg'
  const restore = signIn({
    first_name: 'Анна',
    last_name: 'Иванова',
    photo_url: photo,
  })

  try {
    const { container } = renderApp()
    await user.click(screen.getByRole('button', { name: 'Профиль' }))

    expect(await screen.findByText('Анна Иванова')).toBeTruthy()
    expect(container.querySelector(`img[src="${photo}"]`)).toBeTruthy()
  } finally {
    restore()
  }
})

test('signed-in profile shows the user icon when telegram has no photo', async () => {
  const user = userEvent.setup()
  const restore = signIn({ first_name: 'Борис', last_name: '', photo_url: '' })

  try {
    renderApp()
    await user.click(screen.getByRole('button', { name: 'Профиль' }))

    const name = await screen.findByText('Борис')
    const identity = name.parentElement
    expect(identity?.querySelector('img')).toBeNull()
    expect(identity?.querySelector('svg')).toBeTruthy()
  } finally {
    restore()
  }
})
