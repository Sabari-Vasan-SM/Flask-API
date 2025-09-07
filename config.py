# Bus Ticket Booking API Configuration
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Debug mode settings
    DEBUG = True
    
    # Testing mode flag
    TESTING = False
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///tickets.db'
    
    # Session configuration
    SESSION_PERMANENT = False                    # Sessions expire when browser closes
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Maximum session duration
    
    # API Rate limiting configuration to prevent abuse
    RATELIMIT_ENABLED = True                     # Enable rate limiting
    RATELIMIT_DEFAULT = "100 per hour"          # Default rate limit per user
    
    # Business logic configuration for bus booking system
    MAX_SEATS_PER_BUS = 40                       # Maximum seats per bus
    AVAILABLE_BUSES = [                          # List of available bus numbers
        'BUS001', 'BUS002', 'BUS003', 'BUS004', 'BUS005'
    ]

class DevelopmentConfig(Config):
    """
    Development environment configuration
    
    This configuration is optimized for local development with
    enhanced debugging and relaxed security settings.
    """
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
