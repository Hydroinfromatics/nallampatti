from flask import Blueprint, render_template, current_app

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    port = current_app.config['PORT']
    
    # Content for the home page
    welcome_message = "Every Drop Counts, Every Voice Matters"

    intro_text = "Nallampatti Water Wellness Initiative: Mapping Our Community's Aquatic Health"
    
    features = [
        {
            "title": "Rich Heritage",
            "description": "Explore our centuries-old temples and traditional architecture.",
            "image": "nal.jpg"
        },
        {
            "title": "Natural Beauty",
            "description": "Experience the lush greenery and scenic landscapes surrounding our village.",
            "image": "nal2.jpg"
        },
        {
            "title": "Sensor Installation in Tropical Garden",
            "description": "Natural backdrop showcasing the implementation of sensor technology, implying a blend of nature and modern monitoring systems",
            "image": "nal4.jpeg"
        }
    ]
    
    events = [
        {
            "name": "Real-time Monitoring",
            "description": "A real time water quality monitoring unit was deployed in the Nallampatti village with the initial funds from Aquamap IIT Madras. The Water quality monitoring unit has been installed near a well inside village. Major purpose of real-time monitoring is to keep a track of seasonal changes in water quality for the basic parameters pH, TDS and variations in the ground water level. The unit is future extendible to additional parameters (Nitrate, Hardness, Fluoride, Chloride, DO, Ammonium, Turbidity, etc.) for a detailed real time monitoring of ground water composition and temporal changes in the same."
        }
    ]

    content = render_template(
        'home_content.html',
        welcome_message=welcome_message,
        intro_text=intro_text,
        features=features,
        events=events,
    )

    return render_template('base.html', title="Home", content=content)