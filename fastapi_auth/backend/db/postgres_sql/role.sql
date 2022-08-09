-- name: get_all_roles_and_permissions
SELECT
  r.id,
  r.name,
  COALESCE(array_agg(DISTINCT p.name), ARRAY[]::text[]) AS permissions
FROM
  auth_role r
LEFT JOIN auth_role_permission rp
  ON rp.role_id = r.id
LEFT JOIN auth_permission p
  ON p.id = rp.permission_id
GROUP BY
  r.id;

-- name: create_role
INSERT INTO auth_role (
  name
) VALUES (
  $1
);

-- name: get_role_by_name
SELECT
  id,
  name
FROM
  auth_role
WHERE
  name = $1;

-- name: get_role_and_permissions_by_name
SELECT
  r.id,
  r.name,
  (
    SELECT
      COALESCE(array_agg(DISTINCT p.name), ARRAY[]::text[])
    FROM
      auth_permission p
    JOIN auth_role_permission rp
      ON rp.role_id = r.id
  ) AS permissions
FROM
  auth_role r
WHERE
  r.name = $1
GROUP BY
  r.id;


-- name: create_user_role_relation
INSERT INTO auth_user_role (
  user_id,
  role_id
) VALUES (
  $1,
  $2
)
ON CONFLICT (user_id, role_id) DO NOTHING;

-- name: get_user_role_relation
SELECT
  user_id,
  role_id
FROM
  auth_user_role
WHERE
  user_id = $1
  AND role_id = $2;

-- name: delete_user_role_relation
DELETE FROM
  auth_user_role
WHERE
  user_id = $1
  AND role_id = $2;

-- name: delete_role_by_name
DELETE FROM
  auth_role
WHERE
  name = $1;

-- name: create_permission
INSERT INTO auth_permission (
  name
) VALUES (
  $1
)
RETURNING id;

-- name: get_permission_by_name
SELECT
  id,
  name
FROM
  auth_permission
WHERE
  name = $1;

-- name: create_role_permission_relation
INSERT INTO auth_role_permission (
  role_id,
  permission_id
) VALUES (
  $1, $2
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- name: get_role_permission_relation
SELECT
  user_id,
  role_id
FROM
  auth_user_role
WHERE
  user_id = $1
  AND role_id = $2;

-- name: delete_role_permission_relation
DELETE FROM
  auth_role_permission
WHERE
  role_id = $1
  AND permission_id = $2;

