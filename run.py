import os
from app import create_app

# Set environment variable for port detection in routes
os.environ['FLASK_RUN_PORT'] = '4000'

app = create_app()

if __name__ == '__main__':
    # Default to development mode
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Run the guest interface on port 4000
    app.run(host='0.0.0.0', port=4000)
