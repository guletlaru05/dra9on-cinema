-- Subscription capability only. No email, IP, user agent, analytics ID or history.
CREATE TABLE IF NOT EXISTS push_subscriptions (
 id TEXT PRIMARY KEY, endpoint TEXT NOT NULL UNIQUE, p256dh TEXT NOT NULL,
 auth TEXT NOT NULL, lang TEXT NOT NULL CHECK(lang IN ('ko','en','ja','es')),
 delete_hash TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS push_metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS push_seen (id TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS push_events (id TEXT PRIMARY KEY,payload TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS push_deliveries (
 event_id TEXT NOT NULL REFERENCES push_events(id) ON DELETE CASCADE,
 sub_id TEXT NOT NULL REFERENCES push_subscriptions(id) ON DELETE CASCADE,
 state TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
 lease TEXT, lease_at TEXT, next_attempt_at TEXT NOT NULL,
 PRIMARY KEY(event_id,sub_id)
);
CREATE INDEX IF NOT EXISTS push_delivery_pending ON push_deliveries(state,next_attempt_at);
CREATE TABLE IF NOT EXISTS push_subscription_budget(day TEXT PRIMARY KEY,writes INTEGER NOT NULL);
