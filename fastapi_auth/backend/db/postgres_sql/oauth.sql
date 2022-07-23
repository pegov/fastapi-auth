-- name: create_oauth
INSERT INTO auth_oauth (
  user_id,
  provider,
  sid
) VALUES (
  $1, $2, $3
);

-- name: get_oauth_by_user_id
SELECT
  *
FROM
  auth_oauth
WHERE
  user_id = $1;

-- name: get_oauth_by_provider_and_sid
SELECT
  *
FROM
  auth_oauth
WHERE
  provider = $1
  AND sid = $2;

-- name: update_oauth_by_id
UPDATE
  auth_oauth
SET
  provider = $2,
  sid = $3
WHERE
  id = $1;

-- name: update_oauth_by_user_id
UPDATE
  auth_oauth
SET
  provider = $2,
  sid = $3
WHERE
  user_id = $1;

-- name: delete_oauth_by_id
DELETE FROM
  auth_oauth
WHERE
  id = $1;

-- name: delete_oauth_by_user_id
DELETE FROM
  auth_oauth
WHERE
  user_id = $1;

