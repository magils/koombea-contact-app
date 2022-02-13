from distutils.command.upload import upload
from flask import Blueprint, jsonify, request, Response, jsonify
from app.errors import APIError
from app.models import *
from werkzeug.utils import secure_filename
import json, os
from app.importer import import_contacts
from app.config import AppConfig
from app import db
from sqlalchemy.orm.exc import NoResultFound
import logging
from datetime import datetime

contacts_resource = Blueprint("contacts", __name__)

BASE_PATH = AppConfig.UPLOAD_FOLDER


@contacts_resource.route("/uploads")
def uploads():
    size = request.args.get("size", 50)
    page = request.args.get("page", 1)
    uploads = db.session.query(Upload).paginate(page, size, error_out=False).items
    
    return jsonify({"uploads": [u.to_dict() for u in uploads]})


@contacts_resource.route("/contacts/uploads/<int:upload_id>")
def contact_uploads(upload_id):
    size = request.args.get("size", 35, int)
    page = request.args.get("page", 1, int)

    contacts = db.session.query(Contact).filter_by(upload_id=upload_id).paginate(page, size, error_out=False).items
    resp = {
        "contacts":[c.to_dict() for c in contacts] 
    }
    return jsonify(resp)

    
@contacts_resource.route("/contacts", methods=["POST"])
def contacts():
    if not "file" in request.files:
        raise APIError("Invalid request, file required.")

    fields_mapping_value = request.form.get("fields-mapping")
    fields_mapping = {}

    if fields_mapping_value:
        try:
            fields_mapping = json.loads(fields_mapping_value)
        except json.decoder.JSONDecodeError:
            raise APIError("Invalid request. Malformed JSON.")
            
    file = request.files["file"]
    filename = secure_filename(file.filename)
    save_path = os.path.join(BASE_PATH, filename)
    file.save(save_path)

    #TODO: Create user
    user = db.session.query(User).filter_by(id=1).one()

    import_result = import_contacts(save_path, user, fields_mapping)

    if import_result["import_result"]["failed_lines"] > 0:
        log_time_suffix = datetime.now().strftime("%Y%m%d_%H%m%s")
        failed_number_logger = logging.getLogger('failed-number')
        handler = logging.FileHandler(f'import_failed_numbers_{log_time_suffix}.log')
        failed_number_logger.addHandler(handler)
        
        failed_number_logger.warning(import_result["import_result"]["failures"])

    return jsonify(import_result)
