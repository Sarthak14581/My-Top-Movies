from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 
   

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class Base(DeclarativeBase):
    pass


# CREATE DB
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Movies-info.db"
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True)
    year: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(300))
    rating: Mapped[float] = mapped_column(Float(3))
    ranking: Mapped[str] = mapped_column(String(20))
    review: Mapped[str] = mapped_column(String(300))
    img_url: Mapped[str] = mapped_column(String(500))


with app.app_context():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def home():
    # converting all entries to a list
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    all_movies.reverse()
    i = 1
    for movie in all_movies:
        movie.ranking = i
        i += 1
    return render_template("index.html", movies=all_movies)


# creating flask form
class UpdateForm(FlaskForm):
    rating = StringField(label="Your rating eg.7.5 out of 10", validators=[DataRequired()])
    review = StringField(label="Your review", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route('/edit', methods=["POST", "GET"])
def edit_form():
    update_form = UpdateForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if update_form.validate_on_submit():
        movie.review = update_form.review.data
        movie.rating = update_form.rating.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", update_form=update_form)


@app.route('/delete', methods=["POST", "GET"])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))



# form for adding new movie
class Add(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movies", validators=[DataRequired()])

@app.route('/add', methods=["POST", "GET"])
def add():
    form = Add()
    if form.validate_on_submit():
        title = form.title.data
        params = {
            "api_key": "ba30693b80c5c7ada32d64a67761015f",
            "query": title,
        }
        response = requests.get(url=url, params=params)
        text_response = response.json()
        results = text_response["results"]
        print(response.json())
        return render_template("select.html", results=results)
    return render_template("add.html", form=form)


url = "https://api.themoviedb.org/3/search/movie"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiYTMwNjkzYjgwYzVjN2FkYTMyZDY0YTY3NzYxMDE1ZiIsIm5iZiI6MTcyMjA2MTMyNy4xMTA1ODMsInN1YiI6IjY2YTQ5MDA5ZWYwNzZlNjU2Njg3YzYwNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.c3IRktXNLH-zb1FmBghdACuCj8aGRkQ9eswvLQswIHA"
}

@app.route('/update', methods=["GET", "POST"])
def update_home():
    if request.method == "GET":
        movie_id = request.args.get("id")
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(details_url, headers=headers)
        data = response.json()
        title = data["original_title"]
        new_movie = Movie(title=data["original_title"],
                          img_url=f"https://image.tmdb.org/t/p/w500{data["poster_path"]}",
                          year=data["release_date"],
                          description=data["overview"]
                          )
        db.session.add(new_movie)
        db.session.commit()
        id = db.session.execute(db.select(Movie.id).where(Movie.title == title)).scalar()
        print(id)
        return redirect(url_for("edit_form", id=id))




if __name__ == '__main__':
    app.run(debug=True)