
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User, SitterProfile, ParentProfile, Booking
from logic import get_coords_from_address, sort_sitters_by_distance

app = Flask(__name__)

app.config['SECRET_KEY'] = 'university-project-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///babysitter_hub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    if current_user.is_authenticated and current_user.user_type == 'parent':
        all_sitters = SitterProfile.query.all()
        sitters = sort_sitters_by_distance(current_user.lat, current_user.lng, all_sitters)
        return render_template('index.html', sitters=sitters)
    
    sitters = SitterProfile.query.order_by(SitterProfile.rating.desc()).limit(6).all()
    return render_template('index.html', sitters=sitters)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register/sitter', methods=['GET', 'POST'])
def register_sitter():
    if request.method == 'POST':
        email = request.form.get('email')
        address = request.form.get('address')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register_sitter'))

        lat, lng = get_coords_from_address(address)
        if lat is None:
            flash('Could not verify address. Please be more specific.', 'danger')
            return render_template('register_sitter.html')

        new_user = User(email=email, user_type='sitter', lat=lat, lng=lng, address=address)
        new_user.set_password(request.form.get('password'))
        
        new_profile = SitterProfile(
            user=new_user,
            name=request.form.get('name'),
            hourly_rate=float(request.form.get('hourly_rate')),
            experience_years=int(request.form.get('experience')),
            bio=request.form.get('bio')
        )

        try:
            db.session.add(new_user)
            db.session.add(new_profile)
            db.session.commit()
            flash('Sitter account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('register_sitter.html')

@app.route('/register/parent', methods=['GET', 'POST'])
def register_parent():
    if request.method == 'POST':
        email = request.form.get('email')
        address = request.form.get('address')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register_parent'))

        lat, lng = get_coords_from_address(address)
        if lat is None:
            flash('Could not verify address. Please be more specific.', 'danger')
            return render_template('register_parent.html')

        new_user = User(email=email, user_type='parent', lat=lat, lng=lng, address=address)
        new_user.set_password(request.form.get('password'))

        new_profile = ParentProfile(
            user=new_user,
            name=request.form.get('name'),
            children_count=int(request.form.get('children_count')),
            bio=request.form.get('bio')
        )

        try:
            db.session.add(new_user)
            db.session.add(new_profile)
            db.session.commit()
            flash('Parent account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('register_parent.html')

@app.route('/book/<int:sitter_user_id>')
@login_required
def book_sitter(sitter_user_id):
    if current_user.user_type != 'parent':
        flash('Only parents can book sitters.', 'warning')
        return redirect(url_for('index'))

    new_booking = Booking(parent_id=current_user.id, sitter_id=sitter_user_id)
    db.session.add(new_booking)
    db.session.commit()
    
    flash('Booking request sent successfully!', 'success')
    return redirect(url_for('my_bookings'))

@app.route('/my-bookings')
@login_required
def my_bookings():
    if current_user.user_type == 'parent':
        bookings = Booking.query.filter_by(parent_id=current_user.id).all()
    else:
        bookings = Booking.query.filter_by(sitter_id=current_user.id).all()
    
    return render_template('bookings.html', bookings=bookings)

@app.route('/profile')
@login_required
def profile():
    if current_user.user_type == 'sitter':
        profile_data = current_user.sitter_profile
    else:
        profile_data = current_user.parent_profile
    
    return render_template('profile.html', profile=profile_data)

@app.route('/booking/action/<int:booking_id>/<string:action>')
@login_required
def booking_action(booking_id, action):
    booking = Booking.query.get_or_404(booking_id)
    
    if current_user.id != booking.sitter_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('my_bookings'))

    if action == 'confirm':
        booking.status = 'Confirmed'
        flash("Booking confirmed!", "success")
    elif action == 'decline':
        booking.status = 'Cancelled'
        flash("Booking declined.", "info")
    
    db.session.commit()
    return redirect(url_for('my_bookings'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return "Error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=True)