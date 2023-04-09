from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SECRET_KEY'] = 'BnBNffCpOpoK*97^%&^%7y465HDGFHDGFHDGFHDGFHGFHGFHFdfd2131423423REGFDgfgvdfgvgCCCCCCdfr'
db = SQLAlchemy(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Dummy admin user
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Email {self.email}>'

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email_data = request.form['email']
        new_email = Email(email=email_data)
        db.session.add(new_email)
        db.session.commit()
        return redirect(url_for('thankyou'))
    return render_template('index.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('download_emails'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('download_emails'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/download_emails')
@login_required
def download_emails():
    email_list = Email.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'email'])

    for email in email_list:
        writer.writerow([email.id, email.email])

    output.seek(0)
    return send_file(output, mimetype='text/csv', attachment_filename='email_list.csv', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
