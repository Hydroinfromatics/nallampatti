from flask import Blueprint, render_template

map_bp = Blueprint('map', __name__)

@map_bp.route('/map')
def map():
    map_content = """<div class="map-container">
        <h1>Nallampatti, Erode District, Tamil Nadu</h1>
        <div class="map-wrapper">
            <div id="mapid" style="height: 400px;"></div>
        </div> """
    return render_template('base.html', title="Map of Nallampatti", content=map_content)