from . import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func


class Event(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150))
    #date = db.Column(db.DateTime(timezone=True), default=func.now())
    dateTime = db.Column(db.DateTime(timezone=True))
    location = db.Column(db.String(150))
    category = db.Column(db.String(150))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    #is_Organizer = db.Column(db.Boolean, unique=False, default=True)
    events = db.relationship('Event')
    bookmarkedEvents = db.relationship('Event')
