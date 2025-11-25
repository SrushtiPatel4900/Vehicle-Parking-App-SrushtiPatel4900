from app import create_app, db
from app.models import User, ParkingLot, ParkingSpot, Booking
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()
db.create_all()
print("Database created successfully.")

# 🚨 Create default admin user if not exists
admin_email = 'admin@admin.com'
admin_username = 'admin'  # ✅ Add this
admin_password = 'admin123'  # Default password

if not User.query.filter_by(email=admin_email).first():
    admin_user = User(
        username=admin_username,  # ✅ REQUIRED
        email=admin_email,
        password=generate_password_hash(admin_password),
        is_admin=True
    )
    db.session.add(admin_user)
    db.session.commit()
    print(f"✅ Admin created: {admin_username} / {admin_password}")
else:
    print("Admin user already exists.")
