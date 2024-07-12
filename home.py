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
            "name": "Household survey-1",
            "date": "August, 2022",
            "description": "Our website collects and displays household survey data, offering insights into our community's living conditions and demographics."
        },
        {
            "name": "Household survey-2",
            "date": "October 2023",
            "description": "Our platform gathers and showcases residential data, providing a window into local lifestyles and population trends."
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