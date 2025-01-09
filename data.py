from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///travel.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Departure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    departure_id = db.Column(db.Integer, db.ForeignKey('departure.id'), nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stars = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    nights = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)

    departure = db.relationship('Departure', backref=db.backref('tours', lazy=True))

from data import departures, tours

def seed_data():
    for code, name in departures.items():
        departure = Departure(code=code, name=name)
        db.session.add(departure)

    db.session.commit()

    for tour_id, tour_data in tours.items():
        departure = Departure.query.filter_by(code=tour_data['departure']).first()
        tour = Tour(
            title=tour_data['title'],
            description=tour_data['description'],
            departure_id=departure.id,
            picture=tour_data['picture'],
            price=tour_data['price'],
            stars=tour_data['stars'],
            country=tour_data['country'],
            nights=tour_data['nights'],
            date=tour_data['date']
        )
        db.session.add(tour)

    db.session.commit()

@app.route('/')
def home():
    tours = Tour.query.all()
    return render_template('index.html', tours=tours)

@app.route('/departures/<departure_code>')
def departures_view(departure_code):
    departure = Departure.query.filter_by(code=departure_code).first_or_404()
    tours = departure.tours
    return render_template('departure.html', departure=departure, tours=tours)

@app.route('/tour/<int:tour_id>')
def tour_view(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    departures = Departure.query.all()
    return render_template('tour.html', tour=tour, departures=departures)

if __name__ == '__main__':
    db.create_all()
    seed_data()
    app.run(debug=True)
