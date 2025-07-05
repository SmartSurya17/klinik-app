from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User, Obat, Pasien, Antrian, Tindakan, Resep
from forms import LoginForm, UserForm, ObatForm, PasienForm, AntrianForm, TindakanForm, ResepForm
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import io

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Buat database (jika belum ada)
@app.before_first_request
def create_tables():
    db.create_all()

# Route untuk home
@app.route('/')
def index():
    return render_template('index.html')

# ... (akan dilanjutkan dengan route untuk masing-masing modul)
