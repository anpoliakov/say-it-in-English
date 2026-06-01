-- Users
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    tg_id       BIGINT UNIQUE,                  -- NULL в dev-режиме
    username    VARCHAR(64),
    first_name  VARCHAR(128),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Word categories
CREATE TYPE word_category AS ENUM ('noun','verb','adj','adv','phrase','other');

-- Words dictionary (per user)
CREATE TABLE IF NOT EXISTS words (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    en          VARCHAR(256) NOT NULL,
    ru          VARCHAR(256) NOT NULL DEFAULT '—',
    category    word_category NOT NULL DEFAULT 'other',
    image_key   VARCHAR(512),                   -- MinIO object key
    source      VARCHAR(32) DEFAULT 'manual',   -- manual | auto
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, en)
);

-- Game sessions (для статистики и прогресса)
CREATE TABLE IF NOT EXISTS game_sessions (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score       INTEGER NOT NULL DEFAULT 0,
    words_done  INTEGER NOT NULL DEFAULT 0,
    started_at  TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_words_user   ON words(user_id);
CREATE INDEX IF NOT EXISTS idx_words_en     ON words(user_id, en);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON game_sessions(user_id);
