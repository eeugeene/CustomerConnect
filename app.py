import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
csrf.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default admin user if it doesn't exist
    from models import Admin
    from werkzeug.security import generate_password_hash
    
    if not Admin.query.filter_by(username='admin').first():
        admin_user = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default admin user created: username=admin, password=admin123")

# Import and register views
import views
