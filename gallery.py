from flask import Blueprint, render_template, request, flash
import os

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('/gallery')
def gallery():
    image_folder = os.path.join('static', 'images')
    images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return render_template('gallery.html', images=images)