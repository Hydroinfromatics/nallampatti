from flask import Blueprint, render_template, current_app

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    port = current_app.config['PORT']
    
    # Content for the home page
    welcome_message = "Unraveling the Water-Health-Agriculture Nexus in Rural India"

    intro_text = "Nallampatti Water Wellness Initiative: Mapping Our Community's Aquatic Health"
    
    features = [
        {
            "title": "Rich Heritage",
            "description": "Immerse yourself in our culture as you explore centuries-old temples and traditional architecture. These structures not only showcase our history but also remind us of the timeless importance of harmonious living with our environment.",
            "image": "nal.jpg"
        },
        {
            "title": "Natural Beauty",
            "description": "Experience the lush greenery and scenic landscapes surrounding our village. Our fertile lands are both our pride and our responsibility, as we work to maintain their health alongside our own.",
            "image": "nal2.jpg"
        },
        {
            "title": "Blending Nature and Technology",
            "description": "Witness our innovative approach to environmental monitoring. In our tropical gardens, we've installed cutting-edge sensors, seamlessly integrating modern technology with our natural surroundings. This fusion allows us to gather crucial data on our water quality and its impact on our community's health.",
            "image": "nal4.jpeg"
        }
    ]
    
    events = [
        {
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