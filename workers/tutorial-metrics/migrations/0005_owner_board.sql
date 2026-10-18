-- Separate from visitor episode subscriptions. Never expose a public list.
CREATE TABLE IF NOT EXISTS board_owner_subscriptions (
 id TEXT PRIMARY KEY, endpoint TEXT NOT NULL, p256dh TEXT NOT NULL, auth TEXT NOT NULL,
 lang TEXT NOT NULL, owner_uid TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS board_post_mirror (
 id TEXT PRIMARY KEY, nickname TEXT NOT NULL, title TEXT NOT NULL, topic TEXT NOT NULL,
 created_at TEXT NOT NULL, source_updated_at TEXT NOT NULL, answered INTEGER NOT NULL,
 bucket_id TEXT, seen_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS board_mirror_created ON board_post_mirror(created_at);
CREATE INDEX IF NOT EXISTS board_mirror_bucket ON board_post_mirror(bucket_id);
CREATE TABLE IF NOT EXISTS board_notice_batches (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL, due_at TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS board_batches_due ON board_notice_batches(due_at);
CREATE TABLE IF NOT EXISTS board_notice_deliveries (
 event_id TEXT NOT NULL, sub_id TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
 attempts INTEGER NOT NULL DEFAULT 0, lease TEXT, lease_at TEXT,
 PRIMARY KEY(event_id,sub_id)
);
CREATE TABLE IF NOT EXISTS board_notify_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
