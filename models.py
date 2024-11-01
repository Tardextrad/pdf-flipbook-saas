import uuid
from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from encryption import encryptor

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email_encrypted = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    refresh_token = db.Column(db.String(256), unique=True)
    refresh_token_expiry = db.Column(db.DateTime)
    flipbooks = db.relationship('Flipbook', backref='owner', lazy=True)

    @property
    def email(self):
        return encryptor.decrypt(self.email_encrypted)

    @email.setter
    def email(self, value):
        self.email_encrypted = encryptor.encrypt(value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def generate_refresh_token(self):
        self.refresh_token = str(uuid.uuid4())
        self.refresh_token_expiry = datetime.utcnow() + timedelta(days=30)
        return self.refresh_token
        
    def is_refresh_token_valid(self, token):
        return (self.refresh_token == token and 
                self.refresh_token_expiry and 
                self.refresh_token_expiry > datetime.utcnow())

    def revoke_refresh_token(self):
        self.refresh_token = None
        self.refresh_token_expiry = None

class Flipbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_encrypted = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    unique_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page_count = db.Column(db.Integer, nullable=False, default=0)
    views = db.relationship('PageView', backref='flipbook', lazy=True)

    @property
    def title(self):
        return encryptor.decrypt(self.title_encrypted)

    @title.setter
    def title(self, value):
        self.title_encrypted = encryptor.encrypt(value)

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flipbook_id = db.Column(db.Integer, db.ForeignKey('flipbook.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address_encrypted = db.Column(db.Text)
    page_number = db.Column(db.Integer)

    @property
    def ip_address(self):
        return encryptor.decrypt(self.ip_address_encrypted) if self.ip_address_encrypted else None

    @ip_address.setter
    def ip_address(self, value):
        self.ip_address_encrypted = encryptor.encrypt(value) if value else None
