CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    unit TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0
);
DROP TABLE IF EXISTS Indikator;

CREATE TABLE IF NOT EXISTS Indikator (
    indikator TEXT UNIQUE NOT NULL,
    capaian TEXT NOT NULL,
    kategori TEXT NOT NULL,
    nilai TEXT NOT NULL,      -- JSON stored as TEXT
    year INTEGER NOT NULL,
    bukti TEXT NOT NULL
);
