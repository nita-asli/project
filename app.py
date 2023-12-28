from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'f4cc586c92828a0569cab7c398abdc74'  

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, default=0)

def get_leaderboard():
    leaderboard = User.query.order_by(User.score.desc()).all()
    return leaderboard

def add_player(username, password):
    new_player = User(username=username, password=password)
    db.session.add(new_player)
    db.session.commit()

def get_weather(city):
    api_key = 'YOUR_OPENWEATHERMAP_API_KEY'  # Ganti dengan kunci API cuaca Anda
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {'q': city, 'appid': api_key}

    response = requests.get(base_url, params=params)
    data = response.json()

    weather_info = []
    for forecast in data['list'][:3]:
        date = forecast['dt_txt']
        temperature_day = forecast['main']['temp']
        temperature_night = forecast['main']['temp_min']
        weather_info.append({'date': date, 'temperature_day': temperature_day, 'temperature_night': temperature_night})

    return weather_info

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = request.form['city']
        weather_info = get_weather(city)
        return render_template('home.html', weather_info=weather_info)

    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User.query.filter_by(username=username).first():
            add_player(username, password)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose another username.', 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = user.username
            flash('Login successful. Welcome back!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'error')

    return render_template('login.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():

@app.route('/leaderboard')
def leaderboard():
    leaderboard = get_leaderboard()
    return render_template('leaderboard.html', leaderboard=leaderboard)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logout successful. See you next time!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
