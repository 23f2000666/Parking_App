from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.user import user_bp
    app.register_blueprint(user_bp)

    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html', title='Home')

    return app
