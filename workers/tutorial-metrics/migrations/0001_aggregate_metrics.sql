-- Only numerical aggregates are retained. No individual event, IP, user-agent,
-- cookie, browser identifier, full referrer, query string or form data table.
CREATE TABLE IF NOT EXISTS daily_budget (
  day TEXT PRIMARY KEY,
  events INTEGER NOT NULL CHECK(events >= 0)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS daily_metrics (
  day TEXT NOT NULL,
  path TEXT NOT NULL,
  views INTEGER NOT NULL DEFAULT 0 CHECK(views >= 0),
  copies INTEGER NOT NULL DEFAULT 0 CHECK(copies >= 0),
  entries INTEGER NOT NULL DEFAULT 0 CHECK(entries >= 0),
  ref_direct INTEGER NOT NULL DEFAULT 0,
  ref_google INTEGER NOT NULL DEFAULT 0,
  ref_naver INTEGER NOT NULL DEFAULT 0,
  ref_youtube INTEGER NOT NULL DEFAULT 0,
  ref_instagram INTEGER NOT NULL DEFAULT 0,
  ref_x INTEGER NOT NULL DEFAULT 0,
  ref_other INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(day, path)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS lifetime_metrics (
  path TEXT PRIMARY KEY,
  views INTEGER NOT NULL DEFAULT 0 CHECK(views >= 0),
  copies INTEGER NOT NULL DEFAULT 0 CHECK(copies >= 0),
  entries INTEGER NOT NULL DEFAULT 0 CHECK(entries >= 0),
  ref_direct INTEGER NOT NULL DEFAULT 0,
  ref_google INTEGER NOT NULL DEFAULT 0,
  ref_naver INTEGER NOT NULL DEFAULT 0,
  ref_youtube INTEGER NOT NULL DEFAULT 0,
  ref_instagram INTEGER NOT NULL DEFAULT 0,
  ref_x INTEGER NOT NULL DEFAULT 0,
  ref_other INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS metrics_metadata (
  key TEXT PRIMARY KEY CHECK(key = 'startedAt'),
  value TEXT NOT NULL
) WITHOUT ROWID;
