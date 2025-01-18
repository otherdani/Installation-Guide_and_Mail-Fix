from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
session = Session()
