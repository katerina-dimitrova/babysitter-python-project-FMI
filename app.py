
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User, SitterProfile, ParentProfile, Booking
from logic import (get_coords_from_address, 
                   has_affordable_sitter, 
                   sort_sitters_by_distance, 
                   sort_sitters_by_experience, 
                   calculate_average_price, 
                   search_sitters)
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'university-project-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///babysitter_hub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id: str) -> User:
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index() -> str:
    """Main page displaying sitters with filtering and sorting options."""
    city_query = request.args.get('city', '').strip()
    max_price = request.args.get('max_price', type=float)
    min_exp = request.args.get('min_experience', type=int, default=0)
    sort_option = request.args.get('sort')

    all_sitters = SitterProfile.query.all()

    sitters = search_sitters(all_sitters, city_query, max_price, min_exp)
    
    if sort_option == 'experience':
        sitters = sort_sitters_by_experience(sitters)
    elif sort_option == 'rating':
        sitters = sorted(sitters, key=lambda x: x.rating, reverse=True)
    elif current_user.is_authenticated and current_user.user_type == 'parent':
        print(f"DEBUG: Parent Coords -> {current_user.lat}, {current_user.lng}")
        sitters = sort_sitters_by_distance(current_user.lat, current_user.lng, sitters)
        if sitters:
            print(f"DEBUG: First Sitter Coords -> {sitters[0].user.lat}, {sitters[0].user.lng}")
    else:
        sitters = sorted(sitters, key=lambda x: x.rating, reverse=True)[:6]

    avg_p = calculate_average_price(sitters)
    
    affordable = has_affordable_sitter(sitters, 15.0)

    return render_template('index.html', 
                           sitters=sitters, 
                           avg_price=avg_p, 
                           has_affordable=affordable)

@app.route('/login', methods=['GET', 'POST'])
def login() -> str:
    """Handle user login by verifying credentials and starting a session."""
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
def logout() -> str:
    """Log out the current user and end their session."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register/sitter', methods=['GET', 'POST'])
def register_sitter() -> str:
    """Handle sitter registration by collecting user details and creating a new sitter profile."""
    if request.method == 'POST':
        email = request.form.get('email')
        
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register_sitter'))

        city = request.form.get('city')
        neighborhood = request.form.get('neighborhood', '').strip()
        street = request.form.get('street', '').strip()
        street_number = request.form.get('street_number', '').strip()
        block = request.form.get('block', '').strip()
        entrance = request.form.get('entrance', '').strip()
        
        errors = []
        if not city:
            errors.append("City is mandatory.")
        
        if not neighborhood and not street:
            errors.append("Please provide either a Neighborhood or a Street name.")
        
        if not street_number and not block:
            errors.append("Please provide either a Street Number or a Block number.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register_sitter.html')
        
        address_parts = []
        if street:
            st_line = street.strip()
            if street_number:
                st_line += f" {street_number.strip()}"
            address_parts.append(st_line)
        if neighborhood:
            address_parts.append(neighborhood.strip())
        if block:
            address_parts.append(f"блок {block.strip()}")
            if entrance: 
                address_parts.append(entrance.strip())
        if city:
            address_parts.append(city.strip())

        full_address = ", ".join(address_parts)
        
        lat, lng = get_coords_from_address(full_address)

        if lat is None:
            flash('Could not verify address. Please check your city and street.', 'danger')
            return render_template('register_sitter.html')

        new_user = User(
            email=email, 
            user_type='sitter', 
            lat=lat, 
            lng=lng,
            address = full_address,
            city=city,
            neighborhood=neighborhood,
            street=street,
            street_number=street_number,
            block=block,
            entrance=entrance
        )
        new_user.set_password(request.form.get('password'))
        
        new_profile = SitterProfile(
            user=new_user,
            name=request.form.get('name'),
            phone_number=request.form.get('phone'),
            hourly_rate=max(0, float(request.form.get('hourly_rate'))),
            experience_years=max(0, int(request.form.get('experience'))),
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
def register_parent() -> str:
    """Handle parent registration by collecting user details and creating a new parent profile."""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register_parent'))

        city = request.form.get('city')
        neighborhood = request.form.get('neighborhood', '').strip()
        street = request.form.get('street', '').strip()
        street_number = request.form.get('street_number', '').strip()
        block = request.form.get('block', '').strip()
        entrance = request.form.get('entrance', '').strip()
        
        errors = []
        if not city:
            errors.append("City is mandatory.")
        
        if not neighborhood and not street:
            errors.append("Please provide either a Neighborhood or a Street name.")
        
        if not street_number and not block:
            errors.append("Please provide either a Street Number or a Block number.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register_parent.html')
        
        address_parts = []
        if street:
            st_line = street.strip()
            if street_number:
                st_line += f" {street_number.strip()}"
            address_parts.append(st_line)
        if neighborhood:
            address_parts.append(neighborhood.strip())
        if block:
            address_parts.append(f"block {block.strip()}")
            if entrance: 
                address_parts.append(entrance.strip())
        if city:
            address_parts.append(city.strip())

        
        full_address = ", ".join(address_parts)
        
        lat, lng = get_coords_from_address(full_address)

        if lat is None:
            flash('Could not verify address. Please check your city and street.', 'danger')
            return render_template('register_parent.html')

        new_user = User(
            email=email, 
            user_type='parent', 
            lat=lat, 
            lng=lng,
            address = full_address,
            city=city,
            neighborhood=neighborhood,
            street=street,
            street_number=street_number,
            block=block,
            entrance=entrance
        )
        new_user.set_password(request.form.get('password'))
        
        new_profile = ParentProfile(
            user=new_user,
            name=request.form.get('name'),
            phone_number=request.form.get('phone'),
            children_count=max(1, int(request.form.get('children_count'))), 
            bio=request.form.get('bio')
        )

        try:
            db.session.add(new_user)
            db.session.add(new_profile)
            db.session.commit()
            flash('Parent account created! Please log in to find a sitter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('register_parent.html')

@app.route('/book/<int:sitter_user_id>', methods=['GET', 'POST'])
@login_required
def book_sitter(sitter_user_id: int) -> str:
    """Allow a parent to book a sitter for a specified time period."""
    if current_user.user_type != 'parent':
        flash('Only parents can book sitters.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        start_str = request.form.get('start_time')
        end_str = request.form.get('end_time')
        
        try:
            start_dt = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
            
            if start_dt < datetime.now():
                flash("You cannot book a sitter for a past date or time!", "danger")
                return render_template('book_form.html', sitter_id=sitter_user_id)
            
            if start_dt >= end_dt:
                flash("End time must be after start time.", "danger")
                return render_template('book_form.html', sitter_id=sitter_user_id)

            new_booking = Booking(
                parent_id=current_user.id, 
                sitter_id=sitter_user_id,
                start_time=start_dt,
                end_time=end_dt
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking request sent!', 'success')
            return redirect(url_for('my_bookings'))
        except ValueError:
            flash("Invalid date format.", "danger")

    return render_template('book_form.html', sitter_id=sitter_user_id)

@app.route('/my-bookings')
@login_required
def my_bookings() -> str:
    """Display all bookings for the current user, whether parent or sitter."""
    if current_user.user_type == 'parent':
        bookings = Booking.query.filter_by(parent_id=current_user.id).all()
    else:
        bookings = Booking.query.filter_by(sitter_id=current_user.id).all()
    
    return render_template('bookings.html', bookings=bookings, now=datetime.now())

@app.route('/profile')
@login_required
def profile() -> str:
    """Display the profile of the currently logged-in user."""
    if current_user.user_type == 'sitter':
        profile_data = current_user.sitter_profile
    else:
        profile_data = current_user.parent_profile
    
    return render_template('profile.html', profile=profile_data)

@app.route('/booking/action/<int:booking_id>/<string:action>')
@login_required
def booking_action(booking_id: int, action: str) -> str:
    """Allow sitters to confirm or decline booking requests."""
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

@app.route('/user/<int:user_id>')
@login_required
def view_public_profile(user_id: int) -> str:
    """View the public profile of another user (sitter or parent)."""
    target_user = User.query.get_or_404(user_id)
    if target_user.user_type == 'sitter':
        return render_template('public_profile.html', profile=target_user.sitter_profile, user=target_user)
    else:
        return render_template('public_profile.html', profile=target_user.parent_profile, user=target_user)

@app.route('/booking/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id: int) -> str:
    """Allow parents to cancel their bookings if they haven't started yet."""
    booking = Booking.query.get_or_404(booking_id)
    
    if current_user.id != booking.parent_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('my_bookings'))

    if booking.start_time > datetime.now():
        booking.status = 'Cancelled'
        db.session.commit()
        flash("Booking cancelled successfully.", "info")
    else:
        flash("You cannot cancel a booking that has already started.", "warning")
        
    return redirect(url_for('my_bookings'))

@app.route('/rate-sitter/<int:booking_id>', methods=['POST'])
@login_required
def rate_sitter(booking_id: int) -> str:
    """Allow parents to rate sitters after a completed booking."""
    booking = Booking.query.get_or_404(booking_id)
    new_rating = float(request.form.get('rating'))
    
    if current_user.id == booking.parent_id and booking.end_time < datetime.now():
        sitter = booking.sitter.sitter_profile
        
        total_rating = (sitter.rating * sitter.reviews_count) + new_rating
        sitter.reviews_count += 1
        sitter.rating = round(total_rating / sitter.reviews_count, 1)
        
        booking.status = 'Completed'
        db.session.commit()
        flash(f"Thank you! You rated {sitter.name} with {new_rating} stars.", "success")
        
    return redirect(url_for('my_bookings'))

@app.errorhandler(404)
def page_not_found(e) -> str:
    """Render a custom 404 error page when a page is not found."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e) -> str:
    """Handle internal server errors with a generic message."""
    return "Error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=True)