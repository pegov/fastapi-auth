-- name: create_user
INSERT INTO auth_user (
  email,
  username,
  password,
  active,
  verified,
  created_at,
  last_login
) VALUES ($1, $2, $3, $4, $5, $6, $7)
RETURNING id;

-- name: get_user_by_id
SELECT
  u.id,
  u.email,
  u.username,
  u.password,
  u.active,
  u.verified,
  u.created_at,
  u.last_login,
  o.provider AS oauth_provider,
  o.sid AS oauth_sid,
  (
    SELECT
      COALESCE(array_agg(r.name), ARRAY[]::text[])
    FROM
      auth_role r
    JOIN auth_user_role ur
      ON u.id = ur.user_id
  ) AS roles,
  (
    SELECT
      COALESCE(array_agg(DISTINCT p.name), ARRAY[]::text[])
    FROM
      auth_permission p
    JOIN auth_user_role ur
      ON u.id = ur.user_id
    JOIN auth_role_permission rp
      ON ur.role_id = rp.role_id
  ) AS permissions
FROM
  auth_user u
LEFT JOIN auth_oauth o
  ON u.id = o.user_id
WHERE
  u.id = $1;

-- name: get_user_by_username
SELECT
  u.id,
  u.email,
  u.username,
  u.password,
  u.active,
  u.verified,
  u.created_at,
  u.last_login,
  o.provider AS oauth_provider,
  o.sid AS oauth_sid,
  (
    SELECT
      COALESCE(array_agg(r.name), ARRAY[]::text[])
    FROM
      auth_role r
    JOIN auth_user_role ur
      ON u.id = ur.user_id
  ) AS roles,
  (
    SELECT
      COALESCE(array_agg(DISTINCT p.name), ARRAY[]::text[])
    FROM
      auth_permission p
    JOIN auth_user_role ur
      ON u.id = ur.user_id
    JOIN auth_role_permission rp
      ON ur.role_id = rp.role_id
  ) AS permissions
FROM
  auth_user u
LEFT JOIN auth_oauth o
  ON u.id = o.user_id
WHERE
  u.username = $1;

-- name: get_user_by_email
SELECT
  u.id,
  u.email,
  u.username,
  u.password,
  u.active,
  u.verified,
  u.created_at,
  u.last_login,
  o.provider AS oauth_provider,
  o.sid AS oauth_sid,
  (
    SELECT
      COALESCE(array_agg(r.name), ARRAY[]::text[])
    FROM
      auth_role r
    JOIN auth_user_role ur
      ON u.id = ur.user_id
  ) AS roles,
  (
    SELECT
      COALESCE(array_agg(p.name), ARRAY[]::text[])
    FROM
      auth_permission p
    JOIN auth_user_role ur
      ON u.id = ur.user_id
    JOIN auth_role_permission rp
      ON ur.role_id = rp.role_id
  ) AS permissions
FROM
  auth_user u
LEFT JOIN auth_oauth o
  ON u.id = o.user_id
WHERE
  u.email = $1;

-- name: get_user_by_provider_and_sid
SELECT
  u.id,
  u.email,
  u.username,
  u.password,
  u.active,
  u.verified,
  u.created_at,
  u.last_login,
  o.provider AS oauth_provider,
  o.sid AS oauth_sid,
  (
    SELECT
      COALESCE(array_agg(r.name), ARRAY[]::text[])
    FROM
      auth_role r
    JOIN auth_user_role ur
      ON u.id = ur.user_id
  ) AS roles,
  (
    SELECT
      COALESCE(array_agg(DISTINCT p.name), ARRAY[]::text[])
    FROM
      auth_permission p
    JOIN auth_user_role ur
      ON u.id = ur.user_id
    JOIN auth_role_permission rp
      ON ur.role_id = rp.role_id
  ) AS permissions
FROM
  auth_user u
JOIN auth_oauth o
  ON u.id = o.user_id
WHERE
  o.provider = $1
  AND o.sid = $2;


-- name: update_user_by_id
UPDATE
  auth_user
SET
  $2 = $3
WHERE
  id = $1;

-- name: delete_user_by_id
DELETE FROM
  auth_user
WHERE
  id = $1;

