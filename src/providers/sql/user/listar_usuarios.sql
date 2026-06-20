SELECT 
    id,
    username,
    display_name,
    role,
    email,
    created_at,
    updated_at
FROM users
WHERE deleted_at IS NULL
ORDER BY username ASC;
