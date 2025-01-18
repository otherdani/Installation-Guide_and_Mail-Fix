from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_session import Session


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
session = Session()
