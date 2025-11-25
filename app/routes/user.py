from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import ParkingLot, ParkingSpot, Booking
from app import db
from datetime import datetime

user_bp = Blueprint('user', __name__)

# ------------------ Dashboard ------------------ #
@user_bp.route('/dashboard')
@login_required
def dashboard():
    lots = ParkingLot.query.all()
    return render_template('user/dashboard.html', lots=lots)

# ------------------ Book Parking ------------------ #
@user_bp.route('/book_parking/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def book_parking(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=True).all()

    if request.method == 'POST':
        spot_id = int(request.form['spot_id'])
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time_str = request.form.get('end_time')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M') if end_time_str else None

        if end_time and start_time >= end_time:
            flash("End time must be after start time.")
            return redirect(request.url)
        
        spot = ParkingSpot.query.get(spot_id)
        booking = Booking(
            user_id=current_user.id,
            spot_id=spot_id,
            start_time=start_time,
            end_time=end_time
        )
        # Only calculate cost if end_time is given (at booking time)
        if end_time:
            # Calculate total cost now
            duration = (end_time - start_time).total_seconds() / 3600  # hours
            rate = lot.price_per_hour or 20
            booking.total_cost = round(duration * rate, 2)

            # Free the spot since it’s already completed
            spot.is_occupied = False
            spot.is_available = True
        else:
            # Normal active booking
            spot.is_occupied = True
            spot.is_available = False

        # Mark the selected spot as unavailable
        '''spot = ParkingSpot.query.get(spot_id)
        spot.is_available = False
        spot.is_occupied = True'''

        db.session.add(booking)
        db.session.commit()

        flash("Parking booked successfully!", "success")
        return redirect(url_for('user.my_parking'))

    return render_template('user/book_parking.html', lot=lot, available_spots=available_spots)

# ------------------ My Parking ------------------ #
@user_bp.route('/my_parking')
@login_required
def my_parking():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    return render_template('user/my_parking.html', bookings=bookings)

# ------------------ Release Parking Spot ------------------ #
@user_bp.route('/release_booking/<int:booking_id>', methods=['POST'])
@login_required
def release_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for('user.my_parking'))

    if booking.end_time is not None:
        flash("Booking already released.", "warning")
        return redirect(url_for('user.my_parking'))

    # End booking now
    booking.end_time = datetime.now()
    duration = (booking.end_time - booking.start_time).total_seconds() / 3600
    lot = booking.spot.lot
    rate = lot.price_per_hour if lot.price_per_hour else 20  # fallback rate
    booking.total_cost = round(duration * rate, 2)

    # Free up the spot
    spot = ParkingSpot.query.get(booking.spot_id)
    spot.is_occupied = False
    spot.is_available = True

    db.session.commit()

    flash(f"Slot released. Total cost: ₹{booking.total_cost}", "success")
    return redirect(url_for('user.my_parking'))

# ------------------ Charts ------------------ #
# vehicle_parking_app/app/routes/user.py



@user_bp.route('/confirm_release/<int:booking_id>')
@login_required
def confirm_release(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('user.my_parking'))

    if booking.end_time:
        flash("Booking already completed.", "warning")
        return redirect(url_for('user.my_parking'))

    # Calculate estimated cost
    current_time = datetime.now()
    duration = (current_time - booking.start_time).total_seconds() / 3600
    rate = booking.spot.lot.price_per_hour or 20  # fallback if None
    estimated_cost = round(duration * rate, 2)

    return render_template('user/confirm_release.html', booking=booking, estimated_cost=estimated_cost)

@user_bp.route("/charts")
@login_required
def charts():
    user_id = current_user.id
    bookings = Booking.query.filter_by(user_id=user_id).all()

    active = 0
    released = 0
    total_cost = 0

    for b in bookings:
        if b.end_time is None:
            active += 1
        else:
            released += 1
            total_cost += b.total_cost or 0

    chart_data = {
        "active": active,
        "released": released,
        "total_cost": total_cost
    }

    return render_template("user/charts.html", chart_data=chart_data)

@user_bp.route("/charts/data")
@login_required
def user_chart_data():
    user_id = current_user.id
    bookings = Booking.query.filter_by(user_id=user_id).all()

    active = 0
    released = 0
    total_cost = 0

    for b in bookings:
        if b.end_time is None:
            active += 1
        else:
            released += 1
            total_cost += b.total_cost or 0

    return jsonify({
        "active": active,
        "released": released,
        "total_cost": total_cost
    })

