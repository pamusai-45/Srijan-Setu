import os
from app import create_app, db
from app.seed import seed_database
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    # Auto-seed if database has no users
    if not User.query.first():
        seed_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f" * Srijan Setu running on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
