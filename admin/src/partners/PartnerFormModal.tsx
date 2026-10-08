import { useEffect, useState, type FormEvent } from 'react'
import { partnerTypesApi, type PartnerType } from '../partner-types/partnerTypesApi'
import { partnersApi, type PartnerInput } from './partnersApi'

const emptyForm: PartnerInput = {
  name: '',
  type: '',
  referral_url: '',
  blurb: '',
  logo_path: '',
  is_active: true,
  sort_order: 0,
}

type Props = {
  mode: 'create' | 'edit'
  partnerId?: string
  types: PartnerType[]
  onClose: () => void
  onSaved: () => void
}

export function PartnerFormModal({ mode, partnerId, types, onClose, onSaved }: Props) {
  const [typeOptions, setTypeOptions] = useState<PartnerType[]>(types)
  const [form, setForm] = useState<PartnerInput>(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      let loaded = types
      if (loaded.length === 0) {
        try {
          loaded = await partnerTypesApi.list()
        } catch (err) {
          if (!cancelled) {
            setError(err instanceof Error ? err.message : 'Не удалось загрузить типы партнёров')
            setReady(true)
          }
          return
        }
      }
      if (cancelled) return
      setTypeOptions(loaded)

      if (mode === 'edit' && partnerId) {
        const existing = await partnersApi.get(partnerId)
        if (cancelled) return
        if (!existing) {
          setError('Партнёр не найден')
          setReady(true)
          return
        }
        setForm({
          name: existing.name,
          type: existing.type,
          referral_url: existing.referral_url,
          blurb: existing.blurb,
          logo_path: existing.logo_path,
          is_active: existing.is_active,
          sort_order: existing.sort_order,
        })
      } else {
        setForm({ ...emptyForm, type: loaded[0]?.slug ?? '' })
      }
      setReady(true)
    })()
    return () => {
      cancelled = true
    }
  }, [mode, partnerId, types])

  function setField<K extends keyof PartnerInput>(key: K, value: PartnerInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      if (mode === 'edit' && partnerId) {
        await partnersApi.update(partnerId, form)
      } else {
        await partnersApi.create(form)
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
        aria-label={mode === 'create' ? 'Новый партнёр' : 'Изменить партнёра'}
        className="dialog"
        onClick={(e) => e.stopPropagation()}
      >
        <h2>{mode === 'create' ? 'Новый партнёр' : 'Изменить партнёра'}</h2>
        {!ready ? (
          <p className="quiet">Загрузка…</p>
        ) : error === 'Партнёр не найден' ? (
          <p className="alert" role="alert">
            {error}
          </p>
        ) : (
          <form onSubmit={onSubmit} className="stack">
            <label className="field">
              Имя
              <input
                value={form.name}
                onChange={(e) => setField('name', e.target.value)}
                className="control"
                required
              />
            </label>
            <label className="field">
              Тип
              <select
                value={form.type}
                onChange={(e) => setField('type', e.target.value)}
                className="control"
                required
              >
                {typeOptions.map((type) => (
                  <option key={type.slug} value={type.slug}>
                    {type.topic_label}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              Ссылка
              <input
                value={form.referral_url}
                onChange={(e) => setField('referral_url', e.target.value)}
                className="control"
                required
              />
            </label>
            <label className="field">
              Описание
              <textarea
                value={form.blurb}
                onChange={(e) => setField('blurb', e.target.value)}
                className="control"
                rows={3}
              />
            </label>
            <label className="field">
              Путь к логотипу
              <input
                value={form.logo_path}
                onChange={(e) => setField('logo_path', e.target.value)}
                placeholder="media/partners/logo.jpeg"
                className="control control-mono"
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
                checked={form.is_active}
                onChange={(e) => setField('is_active', e.target.checked)}
              />
              Активен
            </label>
            {error ? (
              <p className="alert" role="alert">
                {error}
              </p>
            ) : null}
            <div className="actions">
              <button type="submit" className="btn-primary">
                Сохранить партнёра
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
