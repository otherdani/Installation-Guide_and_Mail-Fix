from flask import Blueprint, render_template, session

from models import Photo
from helpers import login_required

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route("/gallery/<int:pet_id>", methods=['GET', 'POST'])
@login_required
def gallery(pet_id):
    """Display pet gallery"""
    photos = Photo.query.filter_by(pet_id=pet_id).order_by(Photo.date_uploaded.desc()).all()
    photo_data = [photo.to_dict() for photo in photos]
    return render_template('gallery.html', photos=photo_data)
