import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Babysitter, Parent

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    sitters = Babysitter.query.order_by(Babysitter.rating.desc()).limit(3).all()
    return render_template('index.html', sitters=sitters)

@app.route('/register/sitter', methods=['GET', 'POST'])
def register_sitter():
    if request.method == 'POST':
        try:
            new_sitter = Babysitter(
                name=request.form['name'],
                city=request.form['city'],
                hourly_rate=float(request.form['hourly_rate']),
                experience_years=int(request.form['experience']),
                bio=request.form['bio']
            )
            db.session.add(new_sitter)
            db.session.commit()
            flash('Sitter registration successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('register_sitter.html')

@app.route('/register/parent', methods=['GET', 'POST'])
def register_parent():
    if request.method == 'POST':
        try:
            new_parent = Parent(
                name=request.form['name'],
                city=request.form['city'],
                children_count=int(request.form['children_count']),
                needed_hours_per_week=int(request.form['hours']),
                bio=request.form['bio']
            )
            db.session.add(new_parent)
            db.session.commit()
            flash('Parent registration successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
    return render_template('register_parent.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return "Error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=True)