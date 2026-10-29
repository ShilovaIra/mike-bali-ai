import { useEffect, useRef, useState, type FormEvent } from 'react'
import { apiFetch } from '../auth/authApi'
import { partnerTypesApi, type PartnerType } from '../partner-types/partnerTypesApi'
import { partnersApi, type PartnerInput } from './partnersApi'

const emptyForm: PartnerInput = {
  name: '',
  type: '',
  referral_url: '',
  blurb: '',
  is_active: true,
  sort_order: 0,
}

type Props = {
  mode: 'create' | 'edit'
  partnerId?: string
  types: PartnerType[]
  onClose: () => void
  onSaved: () => void
  onChanged?: () => void
}

type LogoState = {
  previewUrl: string
  uploadToken: string | null
  uploading: boolean
  error: string | null
}

const emptyLogo: LogoState = { previewUrl: '', uploadToken: null, uploading: false, error: null }

const MAX_LOGO_BYTES = 5 * 1024 * 1024
const LOGO_TYPES = ['image/png', 'image/jpeg']

function logoFileProblem(file: File): string | null {
  if (!LOGO_TYPES.includes(file.type)) return 'Только JPEG или PNG'
  if (file.size > MAX_LOGO_BYTES) return 'Файл больше 5 МБ'
  return null
}

export function PartnerFormModal({
  mode,
  partnerId,
  types,
  onClose,
  onSaved,
  onChanged = () => {},
}: Props) {
  const [typeOptions, setTypeOptions] = useState<PartnerType[]>(types)
  const [form, setForm] = useState<PartnerInput>(emptyForm)
  const [logo, setLogo] = useState<LogoState>(emptyLogo)
  const [savedLogoUrl, setSavedLogoUrl] = useState('')
  const [createdId, setCreatedId] = useState<string | undefined>(undefined)
  const [fileInputKey, setFileInputKey] = useState(0)
  const [fileName, setFileName] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const ownedPreview = useRef('')
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
          is_active: existing.is_active,
          sort_order: existing.sort_order,
        })
        let previewUrl = existing.logo_url
        if (!previewUrl && existing.logo_path) {
          const logo = await apiFetch(`/api/partners/${encodeURIComponent(partnerId)}/logo`)
          if (!cancelled && logo.ok) {
            previewUrl = URL.createObjectURL(await logo.blob())
            if (ownedPreview.current) URL.revokeObjectURL(ownedPreview.current)
            ownedPreview.current = previewUrl
          }
        }
        if (cancelled) return
        setLogo({ ...emptyLogo, previewUrl })
        setSavedLogoUrl(previewUrl)
      } else {
        setForm({ ...emptyForm, type: loaded[0]?.slug ?? '' })
      }
      setReady(true)
    })()
    return () => {
      cancelled = true
      if (ownedPreview.current) {
        URL.revokeObjectURL(ownedPreview.current)
        ownedPreview.current = ''
      }
    }
  }, [mode, partnerId, types])

  function setField<K extends keyof PartnerInput>(key: K, value: PartnerInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function onLogoPicked(file: File | undefined) {
    if (!file) return
    const invalid = logoFileProblem(file)
    if (invalid) {
      setLogo((prev) => ({ ...prev, uploadToken: null, error: invalid }))
      return
    }
    setLogo((prev) => ({ ...prev, uploading: true, error: null }))
    try {
      const staged = await partnersApi.uploadLogo(file)
      setLogo({
        previewUrl: staged.preview_url,
        uploadToken: staged.upload_token,
        uploading: false,
        error: null,
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Не удалось загрузить логотип'
      setLogo((prev) => ({ ...prev, uploading: false, error: message }))
    }
  }

  async function removeSavedLogo() {
    const id = partnerId ?? createdId
    if (!id) return
    try {
      await partnersApi.removeLogo(id)
      setSavedLogoUrl('')
      setLogo(emptyLogo)
      setFileName('')
      onChanged()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить логотип')
    }
  }

  function dropPickedLogo() {
    setLogo({ ...emptyLogo, previewUrl: savedLogoUrl })
    setFileName('')
    setFileInputKey((key) => key + 1)
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      let savedId = partnerId ?? createdId
      if (!savedId) {
        savedId = (await partnersApi.create(form)).id
        setCreatedId(savedId)
        onChanged()
      } else {
        await partnersApi.update(savedId, form)
      }
      if (logo.uploadToken) {
        try {
          await partnersApi.linkLogo(savedId, logo.uploadToken)
        } catch (err) {
          const reason = err instanceof Error ? err.message : 'Не удалось привязать логотип'
          setError(
            mode === 'create'
              ? `Партнёр создан, но логотип не загрузился: ${reason}`
              : `Логотип не загрузился: ${reason}`,
          )
          return
        }
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
            <div className="field">
              <span>Логотип</span>
              <div className="logo-row">
                {logo.previewUrl ? (
                  <img src={logo.previewUrl} alt="Предпросмотр логотипа" className="logo-preview" />
                ) : (
                  <span className="logo-preview logo-preview-empty">Нет логотипа</span>
                )}
                <input
                  key={fileInputKey}
                  ref={fileInputRef}
                  id="partner-logo"
                  type="file"
                  accept="image/png,image/jpeg"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    setFileName(file?.name ?? '')
                    void onLogoPicked(file)
                  }}
                  disabled={logo.uploading}
                  className="visually-hidden"
                />
                <div className="logo-actions">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={logo.uploading}
                    className="btn-secondary"
                  >
                    {logo.uploading ? 'Загружаем…' : logo.previewUrl ? 'Заменить файл' : 'Выбрать файл'}
                  </button>
                  {fileName ? <span className="quiet">{fileName}</span> : null}
                  {logo.uploadToken || logo.error ? (
                    <button type="button" onClick={dropPickedLogo} className="btn-text">
                      Убрать файл
                    </button>
                  ) : savedLogoUrl ? (
                    <button type="button" onClick={removeSavedLogo} className="btn-danger">
                      Удалить логотип
                    </button>
                  ) : null}
                </div>
              </div>
              <p className="quiet">JPEG или PNG, до 5 МБ</p>
              {logo.error ? (
                <p className="alert" role="alert">
                  {logo.error}
                </p>
              ) : null}
            </div>
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
              <button type="submit" className="btn-primary" disabled={logo.uploading || logo.error !== null}>
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
