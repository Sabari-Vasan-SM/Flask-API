# Bus Ticket Booking API Configuration
# This file contains all configuration settings for different environments

# Import OS module for environment variables and timedelta for time-based settings
import os
from datetime import timedelta

class Config:
    """
    Base configuration class containing common settings
    
    This class defines default configuration values that are shared
    across all environments (development, testing, production).
    """
    
    # Secret key for session management and CSRF protection
    # In production, this should be set via environment variable for security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Debug mode settings - enables detailed error pages and auto-reload
    DEBUG = True
    
    # Testing mode flag - used for unit tests and automated testing
    TESTING = False
    
    # Database configuration for future expansion to persistent storage
    # Currently using in-memory storage, but ready for SQLite/PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///tickets.db'
    
    # Session configuration for user session management
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
