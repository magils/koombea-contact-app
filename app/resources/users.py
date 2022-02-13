from flask import Blueprint, jsonify, request
from app.errors import APIError
from app import db, bcrypt, jwt
from app.models import User
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt


users_resource = Blueprint("users", __name__)

revoke_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in revoke_tokens

@users_resource.route("/signup", methods=["POST"])
def register():
    json_data = request.get_json()
    
    try:
        email = json_data["email"]
        password = json_data["password"]
        
        if db.session.query(User.id).filter_by(email=email).one_or_none():
            raise APIError(f"An user with email '{email}' already exists")
        
        user = User()
        user.email = email
        user.password = password

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": f"User '{email}'registered successfully."})

    except KeyError as ke:
        raise APIError(f"Missing field: '{ke}'")


@users_resource.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    user = db.session.query(User).filter_by(email=body.get("email")).one_or_none()

    if user and bcrypt.check_password_hash(user.password, body.get("password")):
        token_expires = timedelta(days=1)
        token = create_access_token(identity=user.id, expires_delta=token_expires)
        return jsonify({"token": token})

    return jsonify({"error": "You cannot login. Bad credentials."}), 401

@users_resource.route("/logout", methods=["POST"])
@jwt_required()
def logout():
        jti = get_jwt()['jti']
        revoke_tokens.add(jti)

        return jsonify({'message': 'Successfully logged out'})