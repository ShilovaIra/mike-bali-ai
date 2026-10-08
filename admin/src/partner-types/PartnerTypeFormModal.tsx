import { useEffect, useState, type FormEvent } from 'react'
import { partnerTypesApi, type PartnerType } from './partnerTypesApi'

const emptyForm: PartnerType = {
  slug: '',
  is_menu_visible: true,
  sort_order: 0,
  button_label: '',
  topic_label: '',
  intro: '',
  fallback: '',
  caption_emoji: '',
  caption_cta: '',
  button_template: '',
}

type Props = {
  mode: 'create' | 'edit'
  slug?: string
  onClose: () => void
  onSaved: () => void
}

export function PartnerTypeFormModal({ mode, slug: routeSlug, onClose, onSaved }: Props) {
  const [form, setForm] = useState<PartnerType>(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [ready, setReady] = useState(mode === 'create')

  useEffect(() => {
    if (mode !== 'edit' || !routeSlug) return
    let cancelled = false
    partnerTypesApi.get(routeSlug).then((existing) => {
      if (cancelled) return
      if (!existing) {
        setError('Тип партнёра не найден')
        setReady(true)
        return
      }
      setForm(existing)
      setReady(true)
    })
    return () => {
      cancelled = true
    }
  }, [mode, routeSlug])

  function setField<K extends keyof PartnerType>(key: K, value: PartnerType[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    try {
      if (mode === 'create') {
        await partnerTypesApi.create(form)
      } else if (routeSlug) {
        await partnerTypesApi.update(routeSlug, form)
      }
      onSaved()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить')
    }
  }

  return (
    <div className="scrim" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={mode === 'create' ? 'Новый тип партнёра' : 'Изменить тип партнёра'}
        className="dialog dialog-wide"
        onClick={(e) => e.stopPropagation()}
      >
        <h2>{mode === 'create' ? 'Новый тип партнёра' : 'Изменить тип партнёра'}</h2>
        {!ready ? (
          <p className="quiet">Загрузка…</p>
        ) : mode === 'edit' && error === 'Тип партнёра не найден' ? (
          <p className="alert" role="alert">
            {error}
          </p>
        ) : (
          <form onSubmit={onSubmit} className="stack">
            <label className="field">
              Slug
              <input
                value={form.slug}
                onChange={(e) => setField('slug', e.target.value)}
                className="control control-mono"
                required
              />
            </label>
            <label className="field">
              Порядок
              <input
                type="number"
                value={form.sort_order}
                onChange={(e) => setField('sort_order', Number(e.target.value))}
                className="control"
                required
              />
            </label>
            <label className="check">
              <input
                type="checkbox"
                checked={form.is_menu_visible}
                onChange={(e) => setField('is_menu_visible', e.target.checked)}
              />
              Видно в меню
            </label>
            <label className="field">
              Кнопка меню
              <input
                value={form.button_label}
                onChange={(e) => setField('button_label', e.target.value)}
                className="control"
                required
              />
            </label>
            <label className="field">
              Тема в статистике
              <input
                value={form.topic_label}
                onChange={(e) => setField('topic_label', e.target.value)}
                className="control"
                required
              />
            </label>
            <label className="field">
              Intro
              <textarea
                value={form.intro}
                onChange={(e) => setField('intro', e.target.value)}
                className="control"
                rows={2}
                required
              />
            </label>
            <label className="field">
              Fallback
              <textarea
                value={form.fallback}
                onChange={(e) => setField('fallback', e.target.value)}
                className="control"
                rows={2}
                required
              />
            </label>
            <label className="field">
              Emoji подписи
              <input
                value={form.caption_emoji}
                onChange={(e) => setField('caption_emoji', e.target.value)}
                className="control"
                required
              />
            </label>
            <label className="field">
              CTA подписи
              <input
                value={form.caption_cta}
                onChange={(e) => setField('caption_cta', e.target.value)}
                className="control"
                required
              />
            </label>
            <label className="field">
              Шаблон кнопки
              <input
                value={form.button_template}
                onChange={(e) => setField('button_template', e.target.value)}
                className="control"
                required
              />
            </label>
            {error && error !== 'Тип партнёра не найден' ? (
              <p className="alert" role="alert">
                {error}
              </p>
            ) : null}
            <div className="actions">
              <button type="submit" className="btn-primary">
                Сохранить тип
              </button>
              <button type="button" onClick={onClose} className="btn-secondary">
                Отмена
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
