from app import create_app, db
from app.models import User, ParkingLot, ParkingSpot, Booking

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Makes variables available in the 'flask shell' for easy testing."""
    return {
        'db': db,
        'User': User,
        'ParkingLot': ParkingLot,
        'ParkingSpot': ParkingSpot,
        'Booking': Booking
    }


@app.cli.command('seed')
def seed():
    """Seeds the database with an admin user."""
    print("Seeding database...")
    if User.query.filter_by(is_admin=True).first():
        print("Admin user already exists. Skipping.")
        return

    admin_user = User(username='admin', is_admin=True)
    admin_user.set_password('adminpass')
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully.")
