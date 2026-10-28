CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_source TEXT NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    channel TEXT NOT NULL,
    external_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (channel, external_id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    source TEXT NOT NULL DEFAULT 'unknown',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_conversation_per_user
    ON conversations (user_id)
    WHERE status = 'active';

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS messages_conversation_created
    ON messages (conversation_id, created_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS partner_types (
    slug TEXT PRIMARY KEY,
    is_menu_visible BOOLEAN NOT NULL DEFAULT true,
    sort_order INT NOT NULL DEFAULT 0,
    button_label TEXT NOT NULL,
    topic_label TEXT NOT NULL,
    intro TEXT NOT NULL,
    fallback TEXT NOT NULL,
    caption_emoji TEXT NOT NULL,
    caption_cta TEXT NOT NULL,
    button_template TEXT NOT NULL,
    follow_up_text TEXT NOT NULL DEFAULT ''
);

INSERT INTO partner_types (
    slug,
    is_menu_visible,
    sort_order,
    button_label,
    topic_label,
    intro,
    fallback,
    caption_emoji,
    caption_cta,
    button_template,
    follow_up_text
)
VALUES
(
    'esim',
    true,
    10,
    E'📱 \neSIM',
    '📱 eSIM',
    'Чтобы в любой стране оставаться на связи, можно приобрести eSIM в этом боте:',
    'Пока нет доступного бота для покупки eSIM. Напишите Майку — подскажу, что можно сделать.',
    '📱',
    '⬇️ Купить eSIM ⬇️',
    'Купить eSIM',
    ''
),
(
    'money_exchange',
    true,
    20,
    E'💰 \nОбмен',
    '💰 Обмен',
    'Вот партнёры для обмена:',
    'Пока нет доступных партнёров по обмену. Напишите Майку — подскажу, что можно сделать.',
    '💰',
    '⬇️ Обменять сейчас ⬇️',
    'Обменять с {name}',
    ''
),
(
    'excursions',
    true,
    30,
    E'🇮🇩 \nЭкскурсии',
    '🇮🇩 Экскурсии',
    'Вот партнёры по экскурсиям:',
    'Пока нет доступных партнёров по экскурсиям. Напишите Майку — подскажу, что можно сделать.',
    '🇮🇩',
    '⬇️ Забронировать сейчас ⬇️',
    'Забронировать с {name}',
    ''
),
(
    'visa_service',
    true,
    40,
    E'🪪 \nПомощь с Визой',
    '🪪 Помощь с визой',
    'Вот партнёры по визам:',
    'Пока нет доступных партнёров по визам. Напишите Майку — подскажу, что можно сделать.',
    '🪪',
    '⬇️ Оформить визу ⬇️',
    'Оформить с {name}',
    ''
),
(
    'beauty_service',
    true,
    50,
    E'💇‍♀️ \nБьюти услуги',
    '💇‍♀️ Бьюти услуги',
    'Вот партнёры по бьюти-услугам:',
    'Пока нет доступных партнёров по бьюти-услугам. Напишите Майку — подскажу, что можно сделать.',
    '💇‍♀️',
    '⬇️ Записаться ⬇️',
    'Записаться к {name}',
    ''
),
(
    'vehicle_rent',
    true,
    60,
    E'🛵 \nАренда транспорта',
    '🛵 Аренда транспорта',
    'Вот партнёры по аренде транспорта:',
    'Пока нет доступных партнёров по аренде транспорта. Напишите Майку — подскажу, что можно сделать.',
    '🛵',
    '⬇️ Арендовать сейчас ⬇️',
    'Арендовать у {name}',
    ''
)
ON CONFLICT (slug) DO UPDATE SET
    is_menu_visible = EXCLUDED.is_menu_visible,
    sort_order = EXCLUDED.sort_order,
    button_label = EXCLUDED.button_label,
    topic_label = EXCLUDED.topic_label,
    intro = EXCLUDED.intro,
    fallback = EXCLUDED.fallback,
    caption_emoji = EXCLUDED.caption_emoji,
    caption_cta = EXCLUDED.caption_cta,
    button_template = EXCLUDED.button_template,
    follow_up_text = EXCLUDED.follow_up_text;

CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL REFERENCES partner_types (slug) ON DELETE RESTRICT,
    referral_url TEXT NOT NULL,
    blurb TEXT,
    logo_path TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS partners_type_active_sort
    ON partners (type, sort_order)
    WHERE is_active;

INSERT INTO partners (id, name, type, referral_url, blurb, logo_path, is_active, sort_order)
VALUES
(
    '00000000-0000-4000-8000-000000000001',
    'Mike eSIM',
    'esim',
    'https://t.me/Mike_Bali_eSIM_bot',
    '',
    'media/partners/esim-logo.png',
    true,
    1
),
(
    '00000000-0000-4000-8000-000000000002',
    'Ex24.pro',
    'money_exchange',
    'https://ex24qr.com/wtakeox',
    'Лицензированный обмен валюты. Бали, Вьетнам, ОАЭ, Китай, Таиланд. Переводы по всему миру.',
    'media/partners/ex24pro_logo.png',
    true,
    1
),
(
    '00000000-0000-4000-8000-000000000003',
    'My Bali Trips',
    'excursions',
    'https://mybalitrips.com/?utm_pid=1439',
    'С 2013 года — живые гиды по Бали и Индонезии, не бот. Более 60 000 гостей и проверенные туры.',
    'media/partners/excursion_logo.jpeg',
    true,
    1
),
(
    '00000000-0000-4000-8000-000000000004',
    'Butler Support',
    'visa_service',
    'https://t.me/ButlerSupportBot?start=start-ref_baliguide',
    'Откроем и продлим визу, поможем с визами в другие страны, компанией и KITAS. Апостиль, вилла, IMEI, карта и консьерж.',
    'media/partners/visa_service_logo.png',
    true,
    1
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    type = EXCLUDED.type,
    referral_url = EXCLUDED.referral_url,
    blurb = EXCLUDED.blurb,
    logo_path = EXCLUDED.logo_path,
    is_active = EXCLUDED.is_active,
    sort_order = EXCLUDED.sort_order;

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    snapshot JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (conversation_id)
);

CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS last_inbound_at TIMESTAMPTZ;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS follow_up_blocked_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS topic_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS topic_events_topic_created
    ON topic_events (topic, created_at DESC);

CREATE INDEX IF NOT EXISTS topic_events_user_topic
    ON topic_events (user_id, topic, created_at DESC);

CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    payload_ref TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    attempts INT NOT NULL DEFAULT 0,
    next_retry_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS webhook_events_pending
    ON webhook_events (status, next_retry_at)
    WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS follow_up_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('partner_topic', 'win_back')),
    topic TEXT,
    scheduled_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'claimed', 'sent', 'cancelled', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at TIMESTAMPTZ,
    last_error TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS one_pending_partner_follow_up_per_user
    ON follow_up_jobs (user_id)
    WHERE status = 'pending' AND kind = 'partner_topic';

CREATE UNIQUE INDEX IF NOT EXISTS one_pending_win_back_per_user
    ON follow_up_jobs (user_id)
    WHERE status = 'pending' AND kind = 'win_back';

CREATE INDEX IF NOT EXISTS follow_up_jobs_due
    ON follow_up_jobs (status, scheduled_at)
    WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS partner_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS partner_access (
    partner_user_id UUID NOT NULL REFERENCES partner_users (id) ON DELETE CASCADE,
    partner_id UUID NOT NULL REFERENCES partners (id) ON DELETE CASCADE,
    PRIMARY KEY (partner_user_id, partner_id)
);

CREATE TABLE IF NOT EXISTS partner_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES partners (id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS partner_referral_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    view_id UUID NOT NULL REFERENCES partner_views (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL UNIQUE REFERENCES partners (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS saved_partners (
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    partner_id UUID NOT NULL REFERENCES partners (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, partner_id)
);
