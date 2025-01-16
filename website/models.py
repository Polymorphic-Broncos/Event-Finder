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
    # Events created by the user
    created_events = db.relationship('Event', backref='creator', foreign_keys=[Event.userID])
    # Events bookmarked by the user
    bookmarkedEvents = db.relationship('Event', 
                                     secondary='bookmarks',  # Create a new association table
                                     backref='bookmarked_by')

# Create a new association table for bookmarks
bookmarks = db.Table('bookmarks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', UUID(as_uuid=True), db.ForeignKey('event.id'))
)
