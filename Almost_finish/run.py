from app import create_app
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
        logger.info("Flask application is running on http://127.0.0.1:5000")
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        raise 