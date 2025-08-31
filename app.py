from flask import Flask, render_template
from config import config
from routes import api

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Home route
    @app.route('/')
    def home():
        return render_template('index.html')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "Bus Ticket Booking API"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
