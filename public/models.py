from public import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=False)

class Pasien(db.Model):
    __tablename__ = "pasien"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False)

    rekam_medis = db.relationship("RekamMedis", back_populates="pasien")

    def __repr__(self):
        return f"<Pasien {self.id} - Pasien {self.nama}>"

class RekamMedis(db.Model):
    __tablename__ = 'rekam_medis'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey("pasien.id"), nullable=False)
    sistolik = db.Column(db.Integer, nullable=True)
    diastolik = db.Column(db.Integer, nullable=True)
    bpm = db.Column(db.Integer, nullable=True)
    waktu = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    prev_hash = db.Column(db.String(64), nullable=True)
    current_hash = db.Column(db.String(64), nullable=True)
    is_bp_recorded = db.Column(db.Boolean, default=False)

    pasien = db.relationship("Pasien", back_populates="rekam_medis")

    def __repr__(self):
        return f"<RekamMedis {self.id} - Pasien {self.pasien_id}>"
