from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from tmdb_api import TmDB


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-movies.db"
db = SQLAlchemy(app)
Bootstrap(app)


class EditForm(FlaskForm):
    rating = DecimalField(label='Your Rating Out of 10 e.g. 7.5', validators=[DataRequired(), NumberRange(min=0, max=10)])
    review = StringField(label='Your Review')
    submit = SubmitField(label='Done')


class AddMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField(label='Search')


class Movies(db.Model):
    __tablename__ = "First Table"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    id_no = request.args.get("id_no")
    with app.app_context():
        movie_to_update = Movies.query.get(id_no)
    my_form = EditForm()
    if my_form.validate_on_submit():
        with app.app_context():
            update_movie = Movies.query.get(id_no)
            update_movie.rating = round(my_form.rating.data, 1)
            if my_form.review.data != "":
                update_movie.review = my_form.review.data
            db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", book=movie_to_update, form=my_form)


@app.route('/delete')
def delete():
    id_no = request.args.get("id_no")
    delete_movie = Movies.query.get(id_no)
    db.session.delete(delete_movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["POST", "GET"])
def add():
    my_form = AddMovieForm()
    if my_form.validate_on_submit():
        movie = my_form.title.data
        return redirect(url_for('select', movie=movie))
    return render_template("add.html", form=my_form)


@app.route('/select')
def select():
    movie = request.args.get("movie")
    data = TmDB().search(movie)
    return render_template("select.html", result=data)


@app.route('/added')
def added():
    movie = Movies(title=request.args.get("title"),
                   year=request.args.get("year"),
                   description=request.args.get("discrt"),
                   img_url=f"https://image.tmdb.org/t/p/w500/{request.args.get('img_url')}")
    db.session.add(movie)
    db.session.commit()
    id_no = movie.id
    return redirect(url_for('edit', id_no=id_no))


if __name__ == '__main__':
    app.run(debug=True)
