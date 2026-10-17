-- Aggregate quota only. No URLs, identities, tokens, prompts or source bodies.
CREATE TABLE IF NOT EXISTS private_read_budget(day TEXT PRIMARY KEY, reads INTEGER NOT NULL CHECK(reads>=0));
