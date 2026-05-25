from app import create_app
import os

if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    app = create_app('development')
    app.run(host='localhost', port=5000, debug=True)
