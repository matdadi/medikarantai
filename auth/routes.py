from flask import Blueprint, render_template \
    , request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from public import db
from models.system_models import User
from backoffice.routes import dashboard
from public.routes import index

auth_bp = Blueprint("main", __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "doctor":
                index()
            else:
                dashboard()            
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
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
