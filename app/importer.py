import csv, os, re
from app.models import Contact, Upload, UploadStatus
from app.utils import ValidationError
from app import get_logger, db
from datetime import datetime
from sqlalchemy import exc

logger = get_logger(__name__)

def import_contacts(csv_file_path, user, mapped_fields={}):

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"File '{csv_file_path}' not found")

    NAME_KEY = mapped_fields.get("name", "name")
    BIRTHDATE_KEY = mapped_fields.get("birthdate", "birthdate")
    PHONE_KEY = mapped_fields.get("phone", "phone")
    ADDRESS_KEY = mapped_fields.get("address", "address")
    CREDIT_CARD_KEY = mapped_fields.get("credit_card", "credit card")
    EMAIL_KEY = mapped_fields.get("email", "email")

    failed_contacts = []
    import_result = {}

    with open(csv_file_path) as file:
        csv_file = csv.DictReader(file)

        upload = Upload()
        upload.upload_date = datetime.now()
        # Takes only the file name
        upload.file_name = csv_file_path.split("/")[-1]
        upload.status = UploadStatus.PROCESSING
        upload.user = user

        for line in csv_file:

            name = line.get(NAME_KEY)
            birthdate = line.get(BIRTHDATE_KEY)
            phone = line.get(PHONE_KEY)
            address = line.get(ADDRESS_KEY)
            credit_card = line.get(CREDIT_CARD_KEY)
            email = line.get(EMAIL_KEY)

            try:
                c = Contact()
                c.name = name 
                c.birth_date = birthdate
                c.phone = phone
                c.address = address
                c.credit_card = credit_card
                c.email = email
                c.date_created = datetime.now()
                c.user = user
                c.upload = upload

                db.session.add(c)

                upload.increment_succesful_lines()
            except ValidationError as ve:
                failed_contacts.append({
                    "contact": line,
                    "error": str(ve)
                })
                logger.warning("Invalid data detected: %s" % str(ve))
                upload.increment_failed_lines()
            
        upload.status = UploadStatus.FAILED if not upload.successful_lines else UploadStatus.TERMINATED

        try:
            db.session.add(upload)
            db.session.commit()
        except exc.SQLAlchemyError:
            logger.exception("Error persisting imported contacts")
            db.session.rollback()
    
    import_result["import_result"] = {
        "lines_read": (upload.successful_lines + upload.failed_lines),
        "imported_lines": upload.successful_lines,
        "failed_lines": upload.failed_lines,
        "failures": failed_contacts,
        "import_id": upload.id,
        "date_created": upload.upload_date
    }
    
    return import_result


    