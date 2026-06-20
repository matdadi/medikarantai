from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_medika_rantai_app():
    medika_rantai_app = Flask(__name__)


    medika_rantai_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://medikara_medikara:Dari1sampai1000kenangan@localhost/medikara_db_medika'
    medika_rantai_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    medika_rantai_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(medika_rantai_app)

    from public.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.init_app(medika_rantai_app)

    # Register blueprints
    from public.routes.main import medika_rantai_bp
    medika_rantai_app.register_blueprint(medika_rantai_bp)

    return medika_rantai_app