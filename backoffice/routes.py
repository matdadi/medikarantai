from flask import Blueprint, render_template \
    , jsonify, request, redirect, url_for, flash
from flask_login import login_required
from public import db
from models.medicalrecord_models import RekamMedis, Pasien

backoffice_bp = Blueprint("main", __name__)

# default endpoint
@backoffice_bp.route("/")
@login_required
def dashboard():
    # Ambil semua rekam medis milik pasien tertentu
    rekam_list = RekamMedis.query \
        .filter_by(is_bp_recorded = True
                   ).order_by(RekamMedis.id.asc()).all()
    
    latest_rekam = RekamMedis.query \
        .filter_by(is_bp_recorded = True
                   ).order_by(RekamMedis.id.desc()).first()

    return render_template("backoffice/dashboard.html", rekam_list=rekam_list, latest_rekam = latest_rekam)

@backoffice_bp.route("/dashboard")
@backoffice_bp.route("/home")
def redirect_to_dashboard():
    return redirect(url_for("backoffice.dashboard"))

# patient records
@backoffice_bp.route("/patients", methods=["GET"])
@login_required
def patients():
    # Ambil semua data pasien dari database
    patients = db.session.query(Pasien.id, Pasien.nama).all()
    return render_template("patients.html", patients=patients)

# patient record detail
@backoffice_bp.route("/patient-detail-edit/<string:guid>", methods=["GET"])
def redirect_to_patient_detail_edit(guid):
    # Show the patient detail edit form
    return render_template("patient_detail_edit.html", guid=guid)

@backoffice_bp.route("/submit-patient-detail", methods=["POST"])
def submit_patient_detail():
    fullname = request.form.get("fullname")
    if fullname:
        new_pasien = Pasien(nama=fullname)
        db.session.add(new_pasien)
        db.session.commit()
    return redirect(url_for("backoffice.patients"))

#  patient medical record detail
@backoffice_bp.route("/medical-record-edit/<string:guid>", methods=["GET"])
@login_required
def redirect_to_medical_record_edit(guid):
    pasien = Pasien.query.filter_by(guid = guid).first()
    # Ambil semua rekam medis milik pasien tertentu
    rekam_list = RekamMedis.query \
        .filter_by(pasien_id=pasien.id,
                   is_bp_recorded = True
                   ).all()
    
    latest_rekam = RekamMedis.query \
        .filter_by(pasien_id=pasien.id,
                   is_bp_recorded = True
                   ).order_by(RekamMedis.id.desc()).first()

    return render_template("medical_record_edit.html", medical_reports=rekam_list, patient = pasien, recent_report = latest_rekam)

@backoffice_bp.route("/start-measurement/<string:guid>", methods=["POST"])
@login_required
def start_measurement(guid):
    action = request.form.get("action")

    # Check if pasien exists
    pasien = Pasien.query.filter_by(guid = guid).first()
    if not pasien:
        return jsonify({"error": "Pasien not found"}), 404

    if action == "submit":
        latest_open_record = RekamMedis.query \
            .filter_by(
                    pasien_id = pasien.id,
                    is_bp_recorded = False
                ) \
            .order_by(
                RekamMedis.id.desc()
            ) \
            .first()
        
        if latest_open_record:
            flash("Gagal merekam tekanan darah.", "error")
            return redirect(url_for('backoffice.redirect_to_medical_record_edit', pasien_id = pasien.id))

        # Create new empty measurement record
        new_record = RekamMedis(
            pasien_id=pasien.id,
            sistolik=None,
            diastolik=None,
            bpm=None,
            is_bp_recorded=False
        )

        db.session.add(new_record)
        db.session.commit()


        flash("Recording blood pressure... ", "success")
        return redirect(url_for('backoffice.redirect_to_medical_record_edit', guid = guid))
    
    if action == "cancel":        
        latest_open_record = RekamMedis.query \
            .filter_by(
                    pasien_id = pasien.id,
                    is_bp_recorded = False
                ) \
            .order_by(
                RekamMedis.id.desc()
            ) \
            .first()
        
        if not latest_open_record:
            flash("Tidak ada rekam medis", "error")
            return redirect(url_for('backoffice.redirect_to_medical_record_edit', guid = guid))
        
        db.session.delete(latest_open_record)
        db.session.commit()

        flash("Cancelled", "success")
        return redirect(url_for('backoffice.redirect_to_medical_record_edit', guid = guid))
