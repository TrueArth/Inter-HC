INSERT INTO users (
    username,
    hashed_password,
    display_name,
    role,
    email,
    created_at,
    updated_at
) VALUES (
    #username,
    #hashed_password,
    #display_name,
    #role,
    #email,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
RETURNING id, username, display_name, role, email, created_at, updated_at;
