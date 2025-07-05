from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User, Obat, Pasien

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('admin','Admin'), ('dokter','Dokter'), ('apoteker','Apoteker')])
    submit = SubmitField('Simpan')

class ObatForm(FlaskForm):
    nama = StringField('Nama Obat', validators=[DataRequired()])
    stok = IntegerField('Stok Awal', validators=[DataRequired()])
    satuan = StringField('Satuan', validators=[DataRequired()])
    submit = SubmitField('Simpan')

class PasienForm(FlaskForm):
    nama = StringField('Nama Pasien', validators=[DataRequired()])
    alamat = TextAreaField('Alamat')
    telepon = StringField('Telepon')
    submit = SubmitField('Simpan')

class AntrianForm(FlaskForm):
    pasien_id = SelectField('Pasien', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Tambah Antrian')

    def __init__(self, *args, **kwargs):
        super(AntrianForm, self).__init__(*args, **kwargs)
        self.pasien_id.choices = [(p.id, p.nama) for p in Pasien.query.all()]

class TindakanForm(FlaskForm):
    pasien_id = SelectField('Pasien', coerce=int, validators=[DataRequired()])
    diagnosa = TextAreaField('Diagnosa', validators=[DataRequired()])
    submit = SubmitField('Simpan Tindakan')

    def __init__(self, *args, **kwargs):
        super(TindakanForm, self).__init__(*args, **kwargs)
        self.pasien_id.choices = [(p.id, p.nama) for p in Pasien.query.all()]

# Form untuk menambahkan resep (akan digunakan dalam tindakan)
class ResepForm(FlaskForm):
    obat_id = SelectField('Obat', coerce=int, validators=[DataRequired()])
    jumlah = IntegerField('Jumlah', validators=[DataRequired()])
    submit = SubmitField('Tambahkan ke Resep')

    def __init__(self, *args, **kwargs):
        super(ResepForm, self).__init__(*args, **kwargs)
        self.obat_id.choices = [(o.id, o.nama) for o in Obat.query.all()]
