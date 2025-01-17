from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True, index=True)
    content = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    photo_path = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<News {self.title}>'

class ServicedObject(db.Model):
    __tablename__ = 'serviced_objects'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=True)
    characteristics = db.Column(db.Text, nullable=True)
    square_meters = db.Column(db.Float, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ServicedObject {self.address}>'

class RepairWork(db.Model):
    __tablename__ = 'repair_works'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=True)
    work_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RepairWork {self.address}>'

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    action = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<SystemLog {self.action}>'

class Contacts(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    working_hours = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Contacts {self.email}>' 