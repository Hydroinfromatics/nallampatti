from flask import Blueprint, render_template, current_app

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    port = current_app.config['PORT']
    
    # Content for the home page
    welcome_message = "Welcome to Nallampatti"
    intro_text = "Discover the beauty and culture of our vibrant village in Tamil Nadu, India."
    
    features = [
        {
            "title": "Rich Heritage",
            "description": "Explore our centuries-old temples and traditional architecture.",
            "image": "heritage.jpg"
        },
        {
            "title": "Natural Beauty",
            "description": "Experience the lush greenery and scenic landscapes surrounding our village.",
            "image": "nature.jpg"
        },
        {
            "title": "Local Cuisine",
            "description": "Savor the flavors of authentic Tamil cuisine prepared with love by our community.",
            "image": "cuisine.jpg"
        }
    ]
    
    events = [
        {
            "name": "Annual Temple Festival",
            "date": "August 15-17, 2024",
            "description": "Join us for three days of spiritual celebration and cultural performances."
        },
        {
            "name": "Farmers' Market",
            "date": "Every Saturday",
            "description": "Shop for fresh, locally-grown produce and handmade crafts."
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