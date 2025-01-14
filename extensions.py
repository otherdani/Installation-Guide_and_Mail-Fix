from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
session = Session()
oauth = OAuth()
mail = Mail()
