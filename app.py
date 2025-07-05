import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import pandas as pd
from fpdf import FPDF
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'klinik_secret_key'
app.config['DATABASE'] = 'klinik.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Fungsi Database
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Autentikasi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and user['password'] == password:  # Untuk produksi gunakan password hashing
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                      (username, password, role))
            db.commit()
            flash('Akun berhasil dibuat! Silakan login', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username sudah digunakan', 'danger')
    
    return render_template('auth/register.html')

# Dashboard
@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    # Hitung statistik
    total_pasien = db.execute('SELECT COUNT(*) FROM pasien').fetchone()[0]
    total_obat = db.execute('SELECT COUNT(*) FROM obat').fetchone()[0]
    antrian_hari_ini = db.execute("SELECT COUNT(*) FROM antrian WHERE tanggal = date('now') AND status = 'MENUNGGU'").fetchone()[0]
    
    return render_template('index.html', 
                          total_pasien=total_pasien,
                          total_obat=total_obat,
                          antrian_hari_ini=antrian_hari_ini)

# Modul Obat
@app.route('/obat')
def obat_index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    search = request.args.get('search', '')
    
    if search:
        obat = db.execute("SELECT * FROM obat WHERE nama LIKE ?", ('%'+search+'%',)).fetchall()
    else:
        obat = db.execute("SELECT * FROM obat").fetchall()
    
    return render_template('obat/index.html', obat=obat)

@app.route('/obat/tambah', methods=['GET', 'POST'])
def obat_tambah():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        nama = request.form['nama']
        stok = int(request.form['stok'])
        satuan = request.form['satuan']
        min_stok = int(request.form.get('min_stok', 0))
        
        db = get_db()
        db.execute('INSERT INTO obat (nama, stok, satuan, min_stok) VALUES (?, ?, ?, ?)',
                 (nama, stok, satuan, min_stok))
        db.commit()
        flash('Obat berhasil ditambahkan', 'success')
        return redirect(url_for('obat_index'))
    
    return render_template('obat/tambah.html')

@app.route('/obat/<int:id>/stok_masuk', methods=['GET', 'POST'])
def stok_masuk(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    obat = db.execute('SELECT * FROM obat WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        jumlah = int(request.form['jumlah'])
        keterangan = request.form.get('keterangan', '')
        
        # Update stok
        db.execute('UPDATE obat SET stok = stok + ? WHERE id = ?', (jumlah, id))
        
        # Catat di riwayat
        db.execute('INSERT INTO stok_riwayat (obat_id, jumlah, tipe, keterangan) VALUES (?, ?, ?, ?)',
                 (id, jumlah, 'MASUK', keterangan))
        db.commit()
        
        flash(f'Stok {obat["nama"]} berhasil ditambahkan sebanyak {jumlah}', 'success')
        return redirect(url_for('obat_index'))
    
    return render_template('obat/stok_masuk.html', obat=obat)

@app.route('/obat/export')
def export_obat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    obat = db.execute("SELECT * FROM obat").fetchall()
    df = pd.DataFrame(obat, columns=['id', 'nama', 'stok', 'satuan', 'min_stok'])
    
    # Excel
    if request.args.get('format') == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Stok Obat', index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='stok_obat.xlsx',
            as_attachment=True
        )
    
    # PDF
    elif request.args.get('format') == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.cell(200, 10, txt="Laporan Stok Obat", ln=True, align='C')
        pdf.ln(10)
        
        # Kolom
        col_widths = [60, 30, 30, 40]
        headers = ['Nama Obat', 'Stok', 'Satuan', 'Minimal Stok']
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, txt=header, border=1)
        pdf.ln()
        
        # Data
        for _, row in df.iterrows():
            pdf.cell(col_widths[0], 10, txt=row['nama'], border=1)
            pdf.cell(col_widths[1], 10, txt=str(row['stok']), border=1)
            pdf.cell(col_widths[2], 10, txt=row['satuan'], border=1)
            pdf.cell(col_widths[3], 10, txt=str(row['min_stok']), border=1)
            pdf.ln()
        
        output = io.BytesIO()
        pdf.output(output)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/pdf',
            download_name='stok_obat.pdf',
            as_attachment=True
        )
    
    return redirect(url_for('obat_index'))

# Modul Pasien
@app.route('/pasien')
def pasien_index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    search = request.args.get('search', '')
    
    if search:
        pasien = db.execute("SELECT * FROM pasien WHERE nama LIKE ? OR telepon LIKE ?", 
                          ('%'+search+'%', '%'+search+'%')).fetchall()
    else:
        pasien = db.execute("SELECT * FROM pasien").fetchall()
    
    return render_template('pasien/index.html', pasien=pasien)

@app.route('/pasien/tambah', methods=['GET', 'POST'])
def pasien_tambah():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        nama = request.form['nama']
        alamat = request.form['alamat']
        telepon = request.form['telepon']
        tanggal_lahir = request.form['tanggal_lahir']
        jenis_kelamin = request.form['jenis_kelamin']
        
        db = get_db()
        db.execute('INSERT INTO pasien (nama, alamat, telepon, tanggal_lahir, jenis_kelamin) VALUES (?, ?, ?, ?, ?)',
                 (nama, alamat, telepon, tanggal_lahir, jenis_kelamin))
        db.commit()
        flash('Pasien berhasil didaftarkan', 'success')
        return redirect(url_for('pasien_index'))
    
    return render_template('pasien/tambah.html')

@app.route('/pasien/<int:id>')
def pasien_detail(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    pasien = db.execute('SELECT * FROM pasien WHERE id = ?', (id,)).fetchone()
    riwayat = db.execute('''
        SELECT tindakan.*, user.username AS dokter 
        FROM tindakan 
        JOIN users user ON tindakan.dokter_id = user.id
        WHERE pasien_id = ?
        ORDER BY tanggal DESC
    ''', (id,)).fetchall()
    
    return render_template('pasien/detail.html', pasien=pasien, riwayat=riwayat)

# Modul Antrian
@app.route('/antrian')
def antrian_index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    tanggal = request.args.get('tanggal', datetime.now().strftime('%Y-%m-%d'))
    
    antrian = db.execute('''
        SELECT antrian.*, pasien.nama AS nama_pasien 
        FROM antrian 
        JOIN pasien ON antrian.pasien_id = pasien.id
        WHERE tanggal = ? AND status IN ('MENUNGGU', 'DIPANGGIL')
        ORDER BY nomor ASC
    ''', (tanggal,)).fetchall()
    
    selesai = db.execute('''
        SELECT antrian.*, pasien.nama AS nama_pasien 
        FROM antrian 
        JOIN pasien ON antrian.pasien_id = pasien.id
        WHERE tanggal = ? AND status = 'SELESAI'
        ORDER BY nomor ASC
    ''', (tanggal,)).fetchall()
    
    return render_template('antrian/index.html', 
                          antrian=antrian, 
                          selesai=selesai,
                          tanggal=tanggal)

@app.route('/antrian/tambah', methods=['POST'])
def antrian_tambah():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    pasien_id = request.form['pasien_id']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    
    db = get_db()
    
    # Cek nomor antrian terakhir
    last_no = db.execute('''
        SELECT MAX(nomor) FROM antrian 
        WHERE tanggal = ?
    ''', (tanggal,)).fetchone()[0] or 0
    
    nomor_baru = last_no + 1
    
    db.execute('''
        INSERT INTO antrian (pasien_id, tanggal, nomor, status) 
        VALUES (?, ?, ?, 'MENUNGGU')
    ''', (pasien_id, tanggal, nomor_baru))
    db.commit()
    
    flash('Pasien berhasil ditambahkan ke antrian', 'success')
    return redirect(url_for('antrian_index'))

@app.route('/antrian/<int:id>/panggil')
def antrian_panggil(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    db.execute("UPDATE antrian SET status = 'DIPANGGIL' WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('antrian_index'))

@app.route('/antrian/<int:id>/selesai')
def antrian_selesai(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    db.execute("UPDATE antrian SET status = 'SELESAI' WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('antrian_index'))

# Modul Tindakan & Resep
@app.route('/tindakan')
def tindakan_index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    tindakan = db.execute('''
        SELECT tindakan.*, pasien.nama AS nama_pasien, user.username AS dokter 
        FROM tindakan 
        JOIN pasien ON tindakan.pasien_id = pasien.id
        JOIN users user ON tindakan.dokter_id = user.id
        ORDER BY tanggal DESC
    ''').fetchall()
    
    return render_template('tindakan/index.html', tindakan=tindakan)

@app.route('/tindakan/baru', methods=['GET', 'POST'])
def tindakan_baru():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    
    if request.method == 'POST':
        pasien_id = request.form['pasien_id']
        diagnosa = request.form['diagnosa']
        tindakan = request.form['tindakan']
        dokter_id = session['user_id']
        
        # Buat rekam medis
        cur = db.execute('''
            INSERT INTO tindakan (pasien_id, diagnosa, tindakan, dokter_id) 
            VALUES (?, ?, ?, ?)
        ''', (pasien_id, diagnosa, tindakan, dokter_id))
        tindakan_id = cur.lastrowid
        
        # Proses resep
        for key in request.form:
            if key.startswith('obat_'):
                obat_id = key.split('_')[1]
                jumlah = int(request.form[key])
                
                if jumlah > 0:
                    # Cek stok cukup
                    stok_obat = db.execute('SELECT stok FROM obat WHERE id = ?', (obat_id,)).fetchone()['stok']
                    
                    if jumlah > stok_obat:
                        flash(f'Stok obat tidak cukup! Hanya tersedia {stok_obat}', 'danger')
                        db.rollback()
                        return redirect(url_for('tindakan_baru'))
                    
                    # Kurangi stok
                    db.execute('UPDATE obat SET stok = stok - ? WHERE id = ?', (jumlah, obat_id))
                    
                    # Tambah resep
                    db.execute('''
                        INSERT INTO resep (tindakan_id, obat_id, jumlah) 
                        VALUES (?, ?, ?)
                    ''', (tindakan_id, obat_id, jumlah))
                    
                    # Catat di riwayat stok
                    db.execute('''
                        INSERT INTO stok_riwayat (obat_id, jumlah, tipe, keterangan) 
                        VALUES (?, ?, ?, ?)
                    ''', (obat_id, jumlah, 'KELUAR', f'Resep T#{tindakan_id}'))
        
        db.commit()
        flash('Rekam medis berhasil disimpan', 'success')
        return redirect(url_for('tindakan_index'))
    
    pasien = db.execute("SELECT * FROM pasien").fetchall()
    obat = db.execute("SELECT * FROM obat WHERE stok > 0").fetchall()
    return render_template('tindakan/baru.html', pasien=pasien, obat=obat)

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
