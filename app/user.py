from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import ParkingLot, Booking, ParkingSpot
from app.forms import EmptyForm

user_bp = Blueprint('user', __name__, url_prefix='/user',
                    template_folder='templates')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    form = EmptyForm()
    active_booking = Booking.query.filter_by(
        user_id=current_user.id, end_time=None).first()

    lots_query = db.session.query(
        ParkingLot,
        db.func.count(ParkingSpot.id).label('total_spots'),
        db.func.count(db.case((ParkingSpot.status == 'Available',
                      ParkingSpot.id), else_=None)).label('available_spots')
    ).outerjoin(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id).group_by(ParkingLot.id).all()

    lots_data = [
        {'lot': lot, 'total_spots': total, 'available_spots': available}
        for lot, total, available in lots_query
    ]

    booking_history = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.end_time.isnot(None)
    ).order_by(Booking.start_time.desc()).all()

    return render_template('user/dashboard.html', title='User Dashboard',
                           active_booking=active_booking, lots_data=lots_data,
                           booking_history=booking_history, form=form)


@user_bp.route('/book/<int:lot_id>', methods=['POST'])
@login_required
def book_spot(lot_id):
    form = EmptyForm()
    if form.validate_on_submit():
        if Booking.query.filter_by(user_id=current_user.id, end_time=None).first():
            flash(
                'You already have an active parking spot. Please release it before booking a new one.', 'danger')
            return redirect(url_for('user.dashboard'))

        spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='Available').order_by(
            ParkingSpot.spot_number).first()

        if spot:
            spot.status = 'Occupied'

            new_booking = Booking(user_id=current_user.id, spot_id=spot.id)
            db.session.add(new_booking)
            db.session.commit()
            flash(
                f'Success! You are now parked in Spot #{spot.spot_number} at {spot.lot.name}.', 'success')
        else:
            flash(
                'Sorry, all spots in this lot were just taken. Please try another lot.', 'warning')

    return redirect(url_for('user.dashboard'))


@user_bp.route('/release/<int:booking_id>', methods=['POST'])
@login_required
def release_spot(booking_id):
    form = EmptyForm()
    if form.validate_on_submit():
        booking = Booking.query.filter_by(
            id=booking_id, user_id=current_user.id).first_or_404()

        if booking and booking.end_time is None:
            booking.end_time = datetime.utcnow()

            duration_seconds = (booking.end_time -
                                booking.start_time).total_seconds()
            duration_hours = duration_seconds / 3600
            cost = duration_hours * booking.spot.lot.price_per_hour
            booking.total_cost = max(cost, 0.10)

            booking.spot.status = 'Available'

            db.session.commit()
            flash(
                f'You have vacated the spot. Your total charge is ${booking.total_cost:.2f}.', 'success')
        else:
            flash('This booking has already been closed or is invalid.', 'danger')

    return redirect(url_for('user.dashboard'))
