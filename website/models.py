from email.policy import default
from time import timezone
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

user_project = db.Table('user_project',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('project_id', db.Integer(), db.ForeignKey('project.id'))
)
 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150))
    projects = db.relationship('Project', secondary=user_project, backref='members')
    tickets = db.relationship('Ticket')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(125))
    name = db.Column(db.String(80), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    tickets = db.relationship('Ticket')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.String(80), nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(15))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(25))
    priority = db.Column(db.String(25))
