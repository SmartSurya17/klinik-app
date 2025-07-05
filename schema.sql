CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS obat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    stok INTEGER NOT NULL,
    satuan TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pasien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    alamat TEXT,
    telepon TEXT,
    tanggal_daftar DATE DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS antrian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pasien_id INTEGER,
    tanggal DATE DEFAULT (date('now')),
    status TEXT DEFAULT 'MENUNGGU',
    FOREIGN KEY (pasien_id) REFERENCES pasien(id)
);

CREATE TABLE IF NOT EXISTS tindakan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pasien_id INTEGER,
    diagnosa TEXT,
    tanggal DATE DEFAULT (date('now')),
    FOREIGN KEY (pasien_id) REFERENCES pasien(id)
);

CREATE TABLE IF NOT EXISTS resep (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tindakan_id INTEGER,
    obat_id INTEGER,
    jumlah INTEGER,
    FOREIGN KEY (tindakan_id) REFERENCES tindakan(id),
    FOREIGN KEY (obat_id) REFERENCES obat(id)
);
