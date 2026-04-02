#app.py

"""
Application entry point for Pharma IT Validation.

This module initializes the Flask application using the factory
function and starts the development server when executed directly.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # NOTE: `debug=True` should be disabled in production.
    app.run(debug=True)