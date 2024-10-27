import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_DEBUG', '').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
