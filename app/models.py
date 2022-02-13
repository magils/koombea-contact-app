from wsgiref import validate
from app import db, get_logger
import re
from app.utils import validate_with_pattern, get_card_issuer
from sqlalchemy import UniqueConstraint, exc
from enum import Enum
from datetime import datetime, timedelta
from app import jwt
from app.config import AppConfig
from app import bcrypt


failed_number_logger = get_logger(__name__)

class UploadStatus(Enum):
    ON_HOLD="ON_HOLD"
    PROCESSING="PROCESSING"
    FAILED="FAILED"
    TERMINATED="TERMINATED"
    

class Upload(db.Model):

    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(UploadStatus), nullable=False)
    successful_lines = db.Column(db.Integer, default=0)
    failed_lines = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    contacts = db.relationship("Contact", backref="upload")

    def increment_failed_lines(self):
        if self.failed_lines is None:
            self.failed_lines = 0 
        self.failed_lines += 1
    
    def increment_succesful_lines(self):
        if self.successful_lines is None:
            self.successful_lines = 0 
        self.successful_lines += 1

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except exc.SQLAlchemyError:
            failed_number_logger.exception("Error persisting Upload object")
            db.session.rollback()

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "upload_date": self.upload_date,
            "status": self.status.value,
            "user": self.user_id,
            "lines_imported": self.successful_lines,
            "lines_failed": self.failed_lines
        }

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500), nullable=False)
    _password = db.Column("password" ,db.String(1024), nullable=False)

    contacts = db.relationship("Contact", backref="user")
    uploads = db.relationship("Upload", backref="user")

    def encode_auth_token(self):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=3),
            "iat": datetime.now(),
            "sub": self.id
        }
        return jwt.encode(
            payload,
            AppConfig.SECRET_KEY,
            algorithm="HS256"
        )

    @staticmethod
    def decode_auth_token(token):
        payload = jwt.decode(token,  AppConfig.SECRET_KEY)
        return payload["sub"]

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password, rounds=10)



class Contact(db.Model):

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint('user_id', 'email'),)

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column("name",db.String(255))
    _birth_date = db.Column("birth_date",db.DateTime)
    _phone = db.Column("phone", db.String(30))
    _address = db.Column("address", db.String(768))
    _credit_card = db.Column("credit_card",db.String(256))
    _franchise = db.Column("franchise", db.String(25))
    _email = db.Column("email", db.String(255))
    _date_created = db.Column("date_created", db.DateTime)
    _last_4 = db.Column("last_4", db.String(4))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    upload_id = db.Column(db.Integer, db.ForeignKey("uploads.id"))

    @property
    def name(self):
        return self._name 
    
    @name.setter
    @validate_with_pattern(pattern="name", raise_exception=True)
    def name(self, name):
        self._name = name
    
    @property
    def birth_date(self):
        return self._birth_date.strftime("%Y %B %d") if self._birth_date else self._birth_date

    @birth_date.setter
    @validate_with_pattern(pattern="birth_date")
    def birth_date(self, birthdate):
        if not birthdate:
            self._birth_date = birthdate
            return

        date_format = "%Y-%m-%d" if "-" in birthdate else "%Y%m%d" 
        to_date = datetime.strptime(birthdate, date_format)
        
        self._birth_date = to_date
    
    @property
    def phone(self):
        return self._phone

    @phone.setter
    @validate_with_pattern(pattern="phone")
    def phone(self, phone):
        self._phone = phone

    @property
    def address(self):
        return self._address

    @address.setter
    @validate_with_pattern(pattern="address")
    def address(self, address):
        self._address = address

    @property
    def credit_card(self):
        return self._credit_card

    @credit_card.setter
    def credit_card(self, credit_card):
        if not credit_card:
            self._credit_card = credit_card
            return

        self._credit_card = bcrypt.generate_password_hash(credit_card, rounds=10)
        self._last_4 = credit_card[-4:]
        self._franchise = get_card_issuer(credit_card)
    
    @property
    def franchise(self):
        return self._franchise

    @property
    def email(self):
        return self._email
    
    @email.setter
    @validate_with_pattern(pattern="email")
    def email(self, email):
        self._email = email
        
    
    @property
    def date_created(self):
        return self._date_created
    
    @date_created.setter
    def date_created(self, date_value):
        self._date_created = date_value

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "credit_card": ("*" * 10) + self._last_4,
            "franchise": self.franchise,
            "email": self._email,
            "birthdate": self.birth_date
        }

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except exc.SQLAlchemyError:
            failed_number_logger.exception("Error persisting Contact object")
            db.session.rollback()