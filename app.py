"""
This Flask application follows the Application Factory pattern to enhance modularity, scalability, 
and ease of testing. Instead of creating a global Flask app instance, it uses a factory function 
to create and configure the app dynamically.

Model adapted from:
https://flask.palletsprojects.com/en/latest/patterns/appfactories/
"""

from app_factory import init_app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)
