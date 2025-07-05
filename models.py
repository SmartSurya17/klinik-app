from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))  # admin, dokter, apoteker, dll

    def __repr__(self):
        return f'<User {self.username}>'

class Obat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    stok = db.Column(db.Integer, default=0)
    satuan = db.Column(db.String(20))
    # Harga bisa ditambahkan jika diperlukan

class Pasien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(200))
    telepon = db.Column(db.String(20))
    tanggal_daftar = db.Column(db.DateTime, default=datetime.utcnow)

class Antrian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    nomor_antrian = db.Column(db.Integer)
    status = db.Column(db.String(20), default='menunggu')  # menunggu, dipanggil, selesai

class Tindakan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'))
    dokter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diagnosa = db.Column(db.Text)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    resep = db.relationship('Resep', backref='tindakan', lazy='dynamic')

class Resep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tindakan_id = db.Column(db.Integer, db.ForeignKey('tindakan.id'))
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'))
    jumlah = db.Column(db.Integer)
