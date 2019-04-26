DROP TABLE IF EXISTS urls;
DROP INDEX IF EXISTS url_hash_index;
DROP FUNCTION IF EXISTS i_to_wsb64;

CREATE TABLE urls (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  hash BIGINT NOT NULL,
  short_path VARCHAR(32)
);

CREATE INDEX url_hash_index ON urls (hash);

CREATE FUNCTION i_to_wsb64(BIGINT) RETURNS VARCHAR(32) AS
$$
    SELECT translate(encode(decode(padded_hex, 'hex'), 'base64'), '+/=', '-_')
    FROM (
        SELECT lpad(hex, length(hex) + length(hex) % 2, '0') as padded_hex
        FROM (
            SELECT to_hex($1) AS hex
        ) as sq1
   ) as sq2;
$$
LANGUAGE SQL
IMMUTABLE
LEAKPROOF
STRICT;

/* TODO: Insert like this:
INSERT INTO b64_test (b64) VALUES (i_to_wsb64(lastval()));
*/
