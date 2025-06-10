from flask import Flask
from pathlib import Path

def create_app():
    app = Flask(__name__)
    
    # Ensure the instance folder exists
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app 