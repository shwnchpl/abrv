DROP TABLE IF EXISTS urls;
DROP INDEX IF EXISTS url_hash_index;

CREATE TABLE urls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL,
  hash INTEGER NOT NULL,
  short_path TEXT
);

CREATE INDEX url_hash_index ON urls (hash);
