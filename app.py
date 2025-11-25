from app import create_app  # ✅ app, not vehicle_parking_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
