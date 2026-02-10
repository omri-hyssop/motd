"""File serving for uploaded menu assets."""
import os
from flask import Blueprint, current_app, send_from_directory, abort, Response
from werkzeug.utils import secure_filename

from app.models import Menu

bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')


@bp.get('/<path:filename>')
def get_upload(filename):
    """
    Serve menu uploads.

    Note: This endpoint is intentionally unauthenticated so PDFs/images can be
    embedded in <img>/<iframe> without custom auth headers. Files are only
    served if they are referenced by a Menu row.
    """
    # Only allow serving files within the configured upload folder
    upload_dir = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    safe_name = secure_filename(os.path.basename(filename))
    if not safe_name:
        abort(404)

    # Only serve files that are referenced by a menu
    exists = Menu.query.filter_by(menu_file_path=safe_name).first() is not None
    if not exists:
        abort(404)

    resp: Response = send_from_directory(upload_dir, safe_name, as_attachment=False)
    resp.headers.setdefault("Cache-Control", "private, max-age=300")
    return resp
