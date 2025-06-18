-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    unit TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0
);

-- Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    job_name TEXT NOT NULL,
    current_stage TEXT DEFAULT 'Perencanaan',
    start_date TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
