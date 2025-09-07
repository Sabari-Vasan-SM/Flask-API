# Import Flask framework
from flask import Flask, render_template

# Import configuration settings
from config import config

# Import API routes
from routes import api

def create_app(config_name='development'):
    """
    Create Flask app with given configuration
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Register API routes
    app.register_blueprint(api)
    
    # Home page route
    @app.route('/')
    def home():
        """Serve main page"""
        return render_template('index.html')
    
    # Health check route
    @app.route('/health')
    def health_check():
        """Check if service is running"""
        return {"status": "healthy", "service": "Bus Ticket Booking API"}
    
    return app

# Run app if this file is executed directly
if __name__ == '__main__':
    # Create app instance
    app = create_app()
    
    # Start development server
    app.run(debug=True, host='0.0.0.0', port=5000)
