from app import create_app
from datetime import datetime
import argparse

app = create_app()

# Add template context processors
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()

    app.run(debug=True, port=args.port)
