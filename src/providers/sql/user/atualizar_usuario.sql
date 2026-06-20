UPDATE users
SET 
    display_name = #display_name,
    role = #role,
    email = #email,
    updated_at = CURRENT_TIMESTAMP
WHERE id = #id AND deleted_at IS NULL
RETURNING id, username, display_name, role, email, updated_at;
