
class AppConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECRET_KEY="mySecr3tKEy@123."
    UPLOAD_FOLDER="./tmp"
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://koombea:koombea@0.0.0.0:3306/contacts_db"
    JWT_ERROR_MESSAGE_KEY="Error"

class ProdConfig(AppConfig):
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://koombea:koombea@mysql_db/contacts_db"
    UPLOAD_FOLDER="/tmp"



