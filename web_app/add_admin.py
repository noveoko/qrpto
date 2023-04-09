from app import app, db, Admin
from werkzeug.security import generate_password_hash

def add_admin(username, password):
    new_admin = Admin(username=username)
    new_admin.set_password(password)
    with app.app_context():
        db.session.add(new_admin)
        db.session.commit()
        print(f'Admin user "{username}" added.')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python add_admin.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    add_admin(username, password)
