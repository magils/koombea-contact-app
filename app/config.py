
class AppConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECRET_KEY="mySecr3tKEy@123."
    UPLOAD_FOLDER="/Users/mgil/labs/jobs/koombea/contact-importer/tmp"
    # SQLALCHEMY_DATABASE_URI = "sqlite:///../db.sqlite"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://koombea:koombea@0.0.0.0:3306/contacts_db"
