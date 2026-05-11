from app import app, db, User
import json

with app.app_context():
    users = User.query.all()
    user_list = [{"username": u.username, "email": u.email} for u in users]
    print(json.dumps(user_list, indent=2))
