from app import create_app
from datetime import datetime

app = create_app()

# Add template context processors
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run(debug=True)
