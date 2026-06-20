from flask import Blueprint, render_template \
    , jsonify, request, redirect, url_for, flash
from datetime import datetime
from public.models import RekamMedis, Pasien, User
from public.utils.hash_utils import generate_hash
from public import db
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


medika_rantai_bp = Blueprint("main", __name__)


@medika_rantai_bp.route("/")
@login_required
def index():
    # Ambil semua rekam medis milik pasien tertentu
    rekam_list = RekamMedis.query \
        .filter_by(is_bp_recorded = True
                   ).order_by(RekamMedis.id.asc()).all()
    
    latest_rekam = RekamMedis.query \
        .filter_by(is_bp_recorded = True
                   ).order_by(RekamMedis.id.desc()).first()

    return render_template("index.html", rekam_list=rekam_list, latest_rekam = latest_rekam)

    

@medika_rantai_bp.route("/data-pasien-list")
@login_required
def data_pasien_list():
    return render_template("input_pasien.html")
    
@medika_rantai_bp.route("/api/simpan-bpm", methods=["POST"])
def simpan_bpm():
    # retrieve latest not recorded bp
    unfinished_record = RekamMedis.query \
        .filter_by(is_bp_recorded = False) \
        .order_by(RekamMedis.id.asc()) \
        .first()
    
    if not unfinished_record:
        return jsonify({"error": "no pending measurement found"})

    # retrive request body
    data = request.get_json()  # expects JSON body

    unfinished_record.sistolik = data.get("systol")
    unfinished_record.diastolik = data.get("diastol")
    unfinished_record.bpm = data.get("bpm")
    unfinished_record.waktu = datetime.fromtimestamp(data.get("timestamp"))
    unfinished_record.is_bp_recorded = True

    unfinished_record.prev_hash = unfinished_record.prev_hash \
        if unfinished_record.prev_hash != "" else "00000000000000000000000000000000"

    unfinished_record.current_hash = generate_hash(
        unfinished_record.id,
        unfinished_record.pasien_id,
        unfinished_record.sistolik,
        unfinished_record.diastolik,
        unfinished_record.bpm,
        unfinished_record.waktu,
        unfinished_record.prev_hash
    )

    db.session.commit()
    
    return jsonify({"message": "Measurement recorded", "id": unfinished_record.id}), 200

@medika_rantai_bp.route("/list-pasien", methods=["GET"])
@login_required
def list_pasien():
    # Ambil semua data pasien dari database
    pasien_list = db.session.query(Pasien.id, Pasien.nama).all()
    return render_template("list_pasien.html", pasien_list=pasien_list)

@medika_rantai_bp.route("/rekam/<int:pasien_id>", methods=["GET"])
@login_required
def view_rekam_medis(pasien_id):
    pasien = Pasien.query.filter_by(id = pasien_id).first()
    # Ambil semua rekam medis milik pasien tertentu
    rekam_list = RekamMedis.query \
        .filter_by(pasien_id=pasien_id,
                   is_bp_recorded = True
                   ).all()
    
    latest_rekam = RekamMedis.query \
        .filter_by(pasien_id=pasien_id,
                   is_bp_recorded = True
                   ).order_by(RekamMedis.id.desc()).first()

    return render_template("input_pasien.html", rekam_list=rekam_list, pasien_data = pasien, latest_rekam = latest_rekam)

@medika_rantai_bp.route("/rekam/measure/<int:pasien_id>", methods=["POST"])
@login_required
def measure_bpm(pasien_id):
    action = request.form.get("action")

    if action == "submit":
        # Check if pasien exists
        pasien = Pasien.query.get(pasien_id)
        if not pasien:
            return jsonify({"error": "Pasien not found"}), 404
        
        latest_open_record = RekamMedis.query \
            .filter_by(
                    pasien_id = pasien_id,
                    is_bp_recorded = False
                ) \
            .order_by(
                RekamMedis.id.desc()
            ) \
            .first()
        
        if latest_open_record:
            flash("Gagal merekam tekanan darah.", "error")
            return redirect(url_for('main.view_rekam_medis', pasien_id = pasien_id))

        # Create new empty measurement record
        new_record = RekamMedis(
            pasien_id=pasien_id,
            sistolik=None,
            diastolik=None,
            bpm=None,
            is_bp_recorded=False
        )

        db.session.add(new_record)
        db.session.commit()


        flash("Recording blood pressure... ", "success")
        return redirect(url_for('main.view_rekam_medis', pasien_id = pasien_id))
    
    if action == "cancel":
        # Check if pasien exists
        pasien = Pasien.query.get(pasien_id)
        if not pasien:
            return jsonify({"error": "Pasien not found"}), 404
        
        latest_open_record = RekamMedis.query \
            .filter_by(
                    pasien_id = pasien_id,
                    is_bp_recorded = False
                ) \
            .order_by(
                RekamMedis.id.desc()
            ) \
            .first()
        
        if not latest_open_record:
            flash("Tidak ada rekam medis", "error")
            return redirect(url_for('main.view_rekam_medis', pasien_id = pasien_id))
        
        db.session.delete(latest_open_record)
        db.session.commit()

        flash("Cancelled", "success")
        return redirect(url_for('main.view_rekam_medis', pasien_id = pasien_id))
    
@medika_rantai_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@medika_rantai_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@medika_rantai_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash('Username or email already registered', 'danger')
            return redirect(url_for('main.register'))

        # Create new user with hashed password
        hashed_pw = generate_password_hash(password)
        new_user = User(
            fullname=fullname,
            username=username,
            email=email,
            password=hashed_pw,
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    # If GET, just render the login/register page
    return render_template('login.html')

