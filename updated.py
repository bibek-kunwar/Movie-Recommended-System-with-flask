from flask import Flask, render_template, request, redirect, flash, url_for, session
import os
from flask import jsonify
from flask_login import LoginManager, current_user, login_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fuzzywuzzy import process
import pickle
import ast
import re
import requests
import pandas as pd
movies = pickle.load(open('model/movies_list.pk1', 'rb'))
similarity = pickle.load(open('model/similarity.pk1', 'rb'))


app = Flask(__name__)


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
        movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def fetch_genre(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    genres = [genre['name'] for genre in data['genres']]
    return genres


def fetch_overview(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    return data['overview']


def fetch_releasedate(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    return data['release_date']


def fetch_cast(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=8265bd1679663a7ea12ac168da84d2e8"
    data = requests.get(url).json()
    cast = [member['name'] for member in data['cast'][:3]]
    return cast


def fetch_crew(movie_id, job):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=8265bd1679663a7ea12ac168da84d2e8"
    data = requests.get(url).json()
    crew_members = [member['name']
                    for member in data['crew'] if member['job'] == job][:1]
    if crew_members:
        return crew_members[0]
    else:
        return None


def recommend(movie):
    index = process.extractOne(movie, movies['title'])[2]
    print('Movie Selected: ', movies['title'][index], 'index: ', index)
    print('Searching for recommendations.....')
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_genres = []
    recommended_movie_overviews = []
    recommended_movie_release_dates = []
    recommended_movie_cast = []
    recommended_movie_crew = []
    for i in distances[:11]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_genres.append(", ".join(fetch_genre(movie_id)))
        recommended_movie_overviews.append(fetch_overview(movie_id))
        recommended_movie_release_dates.append(fetch_releasedate(movie_id))
        recommended_movie_cast.append(", ".join(fetch_cast(movie_id)))
        recommended_movie_crew.append(
            "".join(fetch_crew(movie_id, "Director")[0]))

    return recommended_movie_names, recommended_movie_posters, recommended_movie_genres, recommended_movie_overviews, recommended_movie_release_dates, recommended_movie_cast, recommended_movie_crew


# step 1
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
# step 3
app.config['SECRET_KEY'] = 'thissecret'
db.init_app(app)


# sstep 4
login_manager = LoginManager()
login_manager.init_app(app)


# sstep 2


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    movie_type = db.Column(db.String(50), nullable=False)  # new column

    def __repr__(self):
        return f"Post('{self.title}', '{self.rating}', '{self.time}', '{self.image_url}', '{self.movie_type}')"


# step 5


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        rating = request.form['rating']
        time = request.form['time']
        movie_type = request.form['movie_type']
        image = request.files['image']
       # is_admin = True if current_user.is_admin else False

        # Save the image to the static/uploads directory
        image.save(f"static/uploads/{image.filename}")
        post = Post(title=title, rating=rating, time=time, movie_type=movie_type,
                    image_url=f"/static/uploads/{image.filename}")
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html')


@app.route('/delete_post', methods=['POST'])
def delete_post():
    movie_name = request.form['movie_name']
    post = Post.query.filter_by(title=movie_name).first()
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted!', 'success')
    return redirect(url_for('index'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        contact = Contact(name=name, email=email, message=message)
        db.session.add(contact)
        db.session.commit()
        flash('regestered has been successfully')

        # Only show contact messages to admin users
        if current_user.is_authenticated and current_user.is_admin:
            contacts = Contact.query.all()
            return render_template('contact.html', contacts=contacts)
        else:
            return redirect('/contact')
    return render_template('contact.html')


@app.route('/desc', methods=['GET', 'POST'])
def desc():

    return render_template('desc.html')


@app.route('/recommendation', methods=['GET', 'POST'])
def recommend():
    movie_list = movies['title'].values
    status = False
    if request.method == 'POST':
        try:
            if request.form:
                movies_name = request.form['movies']
                if movies_name not in movie_list:

                    message = "Movie not found. Search another movie, please!!"
                    return render_template('recommendation.html', movie_list=movie_list, message=message, status=status)
                status = True
                # index = new_df.loc[new_df['title'] == movie].index

                index = process.extractOne(movies_name, movies['title'])[2]
                print('Movie Selected: ',
                      movies['title'][index], 'index: ', index)
                print('Searching for recommendations.....')
                distances = sorted(
                    list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
                recommended_movie_names = []
                recommended_movie_posters = []
                recommended_movie_genres = []
                recommended_movie_overviews = []
                recommended_movie_releasedates = []
                recommended_movie_cast = []
                recommended_movie_crew = []
                for i in distances[:11]:
                    # fetch the movie poster
                    movie_id = movies.iloc[i[0]].movie_id
                    recommended_movie_posters.append(fetch_poster(movie_id))
                    recommended_movie_names.append(movies.iloc[i[0]].title)
                    recommended_movie_genres.append(
                        ", ".join(fetch_genre(movie_id)))
                    recommended_movie_overviews.append(
                        fetch_overview(movie_id))
                    recommended_movie_releasedates.append(
                        fetch_releasedate(movie_id))
                    recommended_movie_cast.append(
                        ", ".join(fetch_cast(movie_id)))
                    recommended_movie_crew.append(
                        fetch_crew(movie_id, "Director"))

                return render_template('recommendation.html', movies_name=recommended_movie_names, poster=recommended_movie_posters, genre=recommended_movie_genres, overview=recommended_movie_overviews, release_date=recommended_movie_releasedates, cast=recommended_movie_cast, crew=recommended_movie_crew, movie_list=movie_list, status=status)
            else:
                message = "Movie not found. Search another movie,please!!"
                return render_template('recommendation.html', error=error, movie_list=movie_list, message=message, status=status)

        except Exception as e:
            error = {'error': e}
            return render_template('recommendation.html', error=error, movie_list=movie_list, status=status)
    else:
        return render_template('recommendation.html', movie_list=movie_list)
    return render_template('recommendation.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        fname = request.form['fname']
        lname = request.form['lname']
        # Check if user with given email and username already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)).first()
        if existing_user:
            flash(
                'User with this email or username already exists. Enter another Email or username.')
            return redirect(url_for('register'))
         # Check if password is strong enough
         # Check if password is strong enough
        if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+])[0-9a-zA-Z!@#$%^&*()_+]{8,}$', password):
            session['email'] = email
            session['username'] = username
            session['fname'] = fname
            session['lname'] = lname
            flash(
                'Password should be at least 8 characters long and contain alphanumeric')
            return redirect(url_for('register'))

        user = User(username=username, email=email, firstname=fname,
                    lastname=lname, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Regestered has been successfully')
        return redirect('/login')
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect('/')
        else:
            flash('invalid credentails', 'warning')
            return redirect('/login')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
