from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import ParkingLot, ParkingSpot, User, Booking
from app.forms import ParkingLotForm, EmptyForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin',
                     template_folder='templates')


@admin_bp.before_request
@login_required
def before_request():
    """Protects all admin routes by ensuring the user is an admin."""
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('index'))


@admin_bp.route('/dashboard')
def dashboard():
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='Occupied').count()
    total_users = User.query.filter_by(is_admin=False).count()

    active_bookings = Booking.query.filter(Booking.end_time.is_(
        None)).order_by(Booking.start_time.desc()).all()

    stats = {
        'total_lots': total_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': total_spots - occupied_spots,
        'total_users': total_users
    }

    return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats, active_bookings=active_bookings)


@admin_bp.route('/lots')
def manage_lots():
    form = ParkingLotForm()
    delete_form = EmptyForm()
    lots = ParkingLot.query.order_by(ParkingLot.name).all()
    return render_template('admin/manage_lots.html', title='Manage Lots', form=form, delete_form=delete_form, lots=lots)


@admin_bp.route('/lots/add', methods=['POST'])
def add_lot():
    form = ParkingLotForm()
    if form.validate_on_submit():
        new_lot = ParkingLot(
            name=form.name.data,
            location=form.location.data,
            capacity=form.capacity.data,
            price_per_hour=form.price_per_hour.data
        )
        db.session.add(new_lot)
        db.session.flush()
        for i in range(1, form.capacity.data + 1):
            spot = ParkingSpot(spot_number=i, lot_id=new_lot.id)
            db.session.add(spot)
        db.session.commit()
        flash(
            f'Parking lot "{new_lot.name}" and its {new_lot.capacity} spots have been created!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.manage_lots'))


@admin_bp.route('/lots/edit/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    form = ParkingLotForm(obj=lot)
    if form.validate_on_submit():
        lot.name = form.name.data
        lot.location = form.location.data
        lot.price_per_hour = form.price_per_hour.data
        new_capacity = form.capacity.data
        if new_capacity < lot.capacity:
            occupied_in_deleted_range = ParkingSpot.query.filter(
                ParkingSpot.lot_id == lot.id,
                ParkingSpot.spot_number > new_capacity,
                ParkingSpot.status == 'Occupied'
            ).count()
            if occupied_in_deleted_range > 0:
                flash(
                    "Cannot reduce capacity. Spots that would be removed are currently occupied.", 'danger')
                return redirect(url_for('admin.manage_lots'))
            ParkingSpot.query.filter(
                ParkingSpot.lot_id == lot.id, ParkingSpot.spot_number > new_capacity).delete()
        elif new_capacity > lot.capacity:
            for i in range(lot.capacity + 1, new_capacity + 1):
                spot = ParkingSpot(spot_number=i, lot_id=lot.id)
                db.session.add(spot)
        lot.capacity = new_capacity
        db.session.commit()
        flash(f'Parking lot "{lot.name}" has been updated.', 'success')
        return redirect(url_for('admin.manage_lots'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.manage_lots'))


@admin_bp.route('/lots/delete/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    form = EmptyForm()
    if form.validate_on_submit():
        occupied_spots = lot.spots.filter_by(status='Occupied').count()
        if occupied_spots > 0:
            flash(
                f'Cannot delete lot "{lot.name}" because it has occupied spots.', 'danger')
        else:
            db.session.delete(lot)
            db.session.commit()
            flash(f'Parking lot "{lot.name}" has been deleted.', 'success')
    return redirect(url_for('admin.manage_lots'))


@admin_bp.route('/lots/<int:lot_id>/spots')
def view_lot_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = lot.spots.order_by(ParkingSpot.spot_number).all()
    return render_template('admin/view_lot_spots.html', title=f'Spots in {lot.name}', lot=lot, spots=spots)


@admin_bp.route('/users')
def view_users():
    users = User.query.filter_by(is_admin=False).order_by(User.username).all()
    return render_template('admin/view_users.html', title='Registered Users', users=users)
