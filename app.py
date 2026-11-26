import os
from datetime import date
from secrets import token_hex

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-key"), SQLALCHEMY_DATABASE_URI="sqlite:///hotel_bookings.db", SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app)
CSRFProtect(app)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    nightly_rate = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(220), nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(12), unique=True, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    room = db.relationship("Room")

def seed_rooms():
    if Room.query.count() == 0:
        db.session.add_all([
            Room(name="Garden Studio", category="Studio", nightly_rate=4200, capacity=2, description="A calm, light-filled room with a private garden view."),
            Room(name="City View Deluxe", category="Deluxe", nightly_rate=6800, capacity=3, description="A generous room near the heart of the city."),
            Room(name="Family Courtyard Suite", category="Suite", nightly_rate=9900, capacity=5, description="Separate sitting area and space for the whole family."),
            Room(name="Hilltop Suite", category="Suite", nightly_rate=11900, capacity=2, description="A quiet top-floor stay with a wide valley view."),
        ])
        db.session.commit()

@app.route("/")
def home():
    seed_rooms()
    check_in = request.args.get("check_in", "")
    check_out = request.args.get("check_out", "")
    category = request.args.get("category", "")
    rooms = Room.query
    if category:
        rooms = rooms.filter_by(category=category)
    if check_in and check_out:
        try:
            start, end = date.fromisoformat(check_in), date.fromisoformat(check_out)
            if end > start:
                conflicts = db.session.query(Reservation.room_id).filter(Reservation.check_in < end, Reservation.check_out > start).subquery()
                rooms = rooms.filter(~Room.id.in_(conflicts))
        except ValueError:
            flash("Enter valid check-in and check-out dates.", "error")
    return render_template("index.html", rooms=rooms.order_by(Room.nightly_rate).all(), check_in=check_in, check_out=check_out, category=category, today=date.today().isoformat())

@app.post("/reserve/<int:room_id>")
def reserve(room_id):
    seed_rooms()
    room = db.get_or_404(Room, room_id)
    try:
        start = date.fromisoformat(request.form.get("check_in", ""))
        end = date.fromisoformat(request.form.get("check_out", ""))
        guests = int(request.form.get("guests", "1"))
    except (ValueError, TypeError):
        flash("Enter valid dates and guest count.", "error")
        return redirect(url_for("home"))
    if start < date.today() or end <= start or not 1 <= guests <= room.capacity:
        flash("Check dates and guest count, then try again.", "error")
        return redirect(url_for("home"))
    conflict = Reservation.query.filter_by(room_id=room.id).filter(Reservation.check_in < end, Reservation.check_out > start).first()
    if conflict:
        flash("That room was just booked for those dates. Search again.", "error")
        return redirect(url_for("home"))
    reservation = Reservation(reference=token_hex(4).upper(), room=room, check_in=start, check_out=end, guests=guests)
    db.session.add(reservation)
    db.session.commit()
    flash(f"Demo reservation confirmed · reference {reservation.reference}", "success")
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()
    seed_rooms()

if __name__ == "__main__":
    app.run(debug=False)
