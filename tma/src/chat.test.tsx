import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'
import { Chat } from './Chat'

afterEach(() => {
  cleanup()
  delete window.Telegram
})

const mapUrl = 'https://www.google.com/maps/search/?api=1&query=Betelnut+Cafe+Canggu+Bali'

test('a map address in Mike’s bubble is a link and the sentence period stays outside it', () => {
  render(
    <Chat
      messages={[{ id: '1', from: 'mike', text: `Смотри ${mapUrl}.` }]}
      replying={false}
      onSend={() => {}}
    />,
  )

  const link = screen.getByRole('link', { name: mapUrl })
  expect(link.getAttribute('href')).toBe(mapUrl)
  expect(link.closest('p')?.textContent).toBe(`Смотри ${mapUrl}.`)
})

test('a tap inside Telegram opens the link and stays in the mini app', async () => {
  const openLink = vi.fn()
  window.Telegram = { WebApp: { openLink } }
  const user = userEvent.setup()
  render(
    <Chat
      messages={[{ id: '1', from: 'mike', text: mapUrl }]}
      replying={false}
      onSend={() => {}}
    />,
  )

  let stayed = false
  const onClick = (event: MouseEvent) => {
    stayed = event.defaultPrevented
  }
  window.addEventListener('click', onClick)

  await user.click(screen.getByRole('link', { name: mapUrl }))
  window.removeEventListener('click', onClick)

  expect(openLink).toHaveBeenCalledWith(mapUrl, { try_instant_view: false })
  expect(stayed).toBe(true)
})

test('an address in your bubble is a link and the sentence period stays outside it', () => {
  render(
    <Chat
      messages={[{ id: '1', from: 'user', text: `Вот ${mapUrl}.` }]}
      replying={false}
      onSend={() => {}}
    />,
  )

  const link = screen.getByRole('link', { name: mapUrl })
  expect(link.getAttribute('href')).toBe(mapUrl)
  expect(link.closest('p')?.textContent).toBe(`Вот ${mapUrl}.`)
})

test('in a browser a link opens in a new tab', async () => {
  const user = userEvent.setup()
  render(
    <Chat
      messages={[{ id: '1', from: 'mike', text: mapUrl }]}
      replying={false}
      onSend={() => {}}
    />,
  )

  const link = screen.getByRole('link', { name: mapUrl })
  expect(link.getAttribute('target')).toBe('_blank')
  expect(link.getAttribute('href')).toBe(mapUrl)

  let stayed = false
  const onClick = (event: MouseEvent) => {
    stayed = event.defaultPrevented
  }
  window.addEventListener('click', onClick)
  await user.click(link)
  window.removeEventListener('click', onClick)

  expect(stayed).toBe(false)
})
