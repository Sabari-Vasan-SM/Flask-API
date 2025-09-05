# Import Flask framework for web application
from flask import Flask, render_template

# Import configuration settings from config module
from config import config

# Import API routes blueprint from routes module
from routes import api

def create_app(config_name='development'):
    """
    Application factory pattern for creating Flask app instances.
    This allows for easier testing and multiple app configurations.
    
    Args:
        config_name (str): Configuration environment ('development', 'production', etc.)
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask application instance with current module name
    app = Flask(__name__)
    
    # Load configuration settings based on environment
    # This sets up database URLs, secret keys, debug modes, etc.
    app.config.from_object(config[config_name])
    
    # Register API routes blueprint with the application
    # This adds all /api/* endpoints to the app
    app.register_blueprint(api)
    
    # Define home route that serves the main HTML page
    @app.route('/')
    def home():
        """
        Home page route - serves the main bus booking interface
        Returns the index.html template with the booking form
        """
        return render_template('index.html')
    
    # Define health check endpoint for monitoring
    @app.route('/health')
    def health_check():
        """
        Health check endpoint for application monitoring
        Returns JSON response indicating service status
        """
        return {"status": "healthy", "service": "Bus Ticket Booking API"}
    
    # Return the configured Flask application
    return app

# Application entry point - only runs when script is executed directly
if __name__ == '__main__':
    # Create application instance using development configuration
    app = create_app()
    
    # Start the Flask development server
    # debug=True: Enables auto-reload and detailed error pages
    # host='0.0.0.0': Makes server accessible from any IP address
    # port=5000: Sets the server port to 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
