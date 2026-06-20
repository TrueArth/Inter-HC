UPDATE users
SET 
    display_name = COALESCE(#display_name, display_name),
    role = COALESCE(#role, role),
    email = COALESCE(#email, email),
    hashed_password = COALESCE(#hashed_password, hashed_password),
    updated_at = CURRENT_TIMESTAMP
WHERE id = #id AND deleted_at IS NULL
RETURNING id, username, display_name, role, email, updated_at;
