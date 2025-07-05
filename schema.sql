CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'dokter', 'apoteker', 'perawat'))
);

CREATE TABLE IF NOT EXISTS obat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0,
    satuan TEXT NOT NULL,
    min_stok INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS stok_riwayat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obat_id INTEGER NOT NULL,
    jumlah INTEGER NOT NULL,
    tipe TEXT NOT NULL CHECK(tipe IN ('MASUK', 'KELUAR')),
    keterangan TEXT,
    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (obat_id) REFERENCES obat(id)
);

CREATE TABLE IF NOT EXISTS pasien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    alamat TEXT,
    telepon TEXT,
    tanggal_lahir DATE,
    jenis_kelamin TEXT CHECK(jenis_kelamin IN ('L', 'P')),
    tanggal_daftar DATE DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS antrian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pasien_id INTEGER NOT NULL,
    tanggal DATE NOT NULL DEFAULT (date('now')),
    nomor INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('MENUNGGU', 'DIPANGGIL', 'SELESAI')) DEFAULT 'MENUNGGU',
    FOREIGN KEY (pasien_id) REFERENCES pasien(id)
);

CREATE TABLE IF NOT EXISTS tindakan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pasien_id INTEGER NOT NULL,
    diagnosa TEXT NOT NULL,
    tindakan TEXT,
    dokter_id INTEGER NOT NULL,
    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pasien_id) REFERENCES pasien(id),
    FOREIGN KEY (dokter_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS resep (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tindakan_id INTEGER NOT NULL,
    obat_id INTEGER NOT NULL,
    jumlah INTEGER NOT NULL,
    FOREIGN KEY (tindakan_id) REFERENCES tindakan(id),
    FOREIGN KEY (obat_id) REFERENCES obat(id)
);

-- Data awal
INSERT OR IGNORE INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('dokter', 'dokter123', 'dokter'),
('apoteker', 'apoteker123', 'apoteker');

INSERT OR IGNORE INTO obat (nama, stok, satuan, min_stok) VALUES
('Paracetamol', 100, 'tablet', 20),
('Amoxicillin', 50, 'kapsul', 15),
('Vitamin C', 200, 'tablet', 30);
