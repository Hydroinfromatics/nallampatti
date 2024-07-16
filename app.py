from flask import Flask
from home import home_bp
from insights import insights_bp
from dashboard import dashboard_bp
from contact import contact_bp
from gallery import gallery_bp
from iot import iot_bp
app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(insights_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(gallery_bp)
app.register_blueprint(iot_bp)

port = 6060  # You can change this to any port number you want
app.config['PORT'] = port

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
    print(f"Application is running on port {port}")