from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import ParkingLot, ParkingSpot, User, db, Booking
from app import db
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    lots = ParkingLot.query.all()
    total_earnings = db.session.query(func.sum(Booking.total_cost))\
                        .filter(Booking.end_time.isnot(None))\
                        .scalar() or 0.0

    return render_template('admin/dashboard.html', lots=lots, total_earnings=total_earnings)

@admin_bp.route('/add_lot', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lot():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        total_spots = int(request.form['total_spots'])

        new_lot = ParkingLot(name=name, location=location, total_spots=total_spots)
        db.session.add(new_lot)
        db.session.commit()

        # Add empty parking spots
        for i in range(1, total_spots + 1):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=f"SPOT-{i}")
            db.session.add(spot)
        db.session.commit()

        flash("Parking lot and spots added.")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_lot.html')

@admin_bp.route('/view_lots')
@login_required
@admin_required
def view_lots():
    lots = ParkingLot.query.all()
    return render_template('admin/view_lots.html', lots=lots)

'''@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.name = request.form['name']
        lot.location = request.form['location']
        db.session.commit()
        flash("Parking lot updated.")
        return redirect(url_for('admin.view_lots'))

    return render_template('admin/edit_lot.html', lot=lot)
'''
@admin_bp.route('/view_users')
@login_required
@admin_required
def view_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/view_users.html', users=users)

@admin_bp.route('/view_spots/<int:lot_id>')
@login_required
@admin_required
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
    return render_template('admin/view_spots.html', lot=lot, spots=spots)



@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_location = request.form.get('location')
        new_total_spots = int(request.form.get('total_spots'))
        new_price = float(request.form.get('price_per_hour'))

        current_spots = len(lot.spots)
        delta = new_total_spots - current_spots

        # Update lot info
        lot.name = new_name
        lot.location = new_location
        lot.total_spots = new_total_spots
        lot.price_per_hour = new_price
        db.session.commit()

        # Add or remove spots
        if delta > 0:
            for i in range(delta):
                new_spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"SPOT-{current_spots + i + 1}",
                    is_available=True
                )
                db.session.add(new_spot)
        elif delta < 0:
            removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=True).limit(-delta).all()
            for spot in removable_spots:
                db.session.delete(spot)

        db.session.commit()
        flash("Parking Lot updated successfully!", "success")
        return redirect(url_for('admin.view_lots'))

    return render_template('admin/edit_lot.html', lot=lot)

# Delete Parking Lot
'''@admin_bp.route('/delete_lot/<int:lot_id>', methods=['POST'])
@login_required
def delete_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)
    for spot in lot.spots:
        db.session.delete(spot)
    db.session.delete(lot)
    db.session.commit()
    flash("Parking Lot deleted successfully!", "success")
    return redirect(url_for('admin.view_lots'))'''
@admin_bp.route('/delete_lot/<int:lot_id>', methods=['GET'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # Check if any spot in the lot is occupied
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=False).first()

    if occupied_spots:
        flash('Cannot delete lot. Some spots are still occupied.', 'danger')
        return redirect(url_for('admin.view_lots'))

    # Optional: delete all spots first (if cascading is not set)
    ParkingSpot.query.filter_by(lot_id=lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin.view_lots'))

@admin_bp.route('/charts')
@login_required
@admin_required
def charts():
    return render_template('admin/charts.html')


@admin_bp.route('/charts/data')
@login_required
@admin_required
def chart_data():
    lots = ParkingLot.query.all()
    lot_names = []
    booked_counts = []
    available_counts = []

    for lot in lots:
        total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        available = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=True).count()
        booked = total_spots - available

        lot_names.append(lot.name)
        booked_counts.append(booked)
        available_counts.append(available)

    return jsonify({
        'lot_names': lot_names,
        'booked_counts': booked_counts,
        'available_counts': available_counts
    })

