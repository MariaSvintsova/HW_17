# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genre')


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        try:
            director_id = request.args.get('director_id')
            genre_id = request.args.get('genre_id')
            if not director_id and not genre_id:
                all_movies = Movie.query.all()
                return movies_schema.dump(all_movies), 200
            elif director_id:
                all = Movie.query.join(Director, Director.id == Movie.director_id).filter(director_id == Director.id).all()
                return movies_schema.dump(all), 200
            else:
                all_genre = Movie.query.join(Genre, Genre.id == Movie.genre_id).filter(genre_id == Genre.id).all()
                return movies_schema.dump(all_genre), 200
        except Exception:
            return 404
    def post(self):
        try:
            new_film = request.json
            film = Movie(**new_film)
            db.session.add(film)
            db.session.commit()
            return movie_schema.dump(film), 200
        except Exception:
            return 404


@movies_ns.route('/<int:id>')
class MoviesView(Resource):
    def get(self, id):
        try:
            movie = Movie.query.get(id)
            if not movie:
                return '', 404
            return movie_schema.dump(movie), 200
        except Exception:
            return 404

    def put(self, id):
        try:
            movie = Movie.query.get(id)
            req_json = request.json

            movie.title = req_json.get('title')
            movie.description = req_json.get('description')
            movie.trailer = req_json.get('trailer')
            movie.year = req_json.get('year')
            movie.rating = req_json.get('rating')
            movie.genre_id = req_json.get('genre_id')
            movie.director_id = req_json.get('director_id')

            db.session.add(movie)
            db.session.commit()
            return '', 204
        except Exception:
            return 404

    def delete(self, id):
        try:
            movie = Movie.query.get(id)
            db.session.delete(movie)
            db.session.commit()
            return '', 200
        except Exception:
            return 404


@directors_ns.route('/')
class DirectorView(Resource):
    def get(self):
        try:
            all_directors = Director.query.all()
            return directors_schema.dump(all_directors), 200
        except Exception:
            return 404

    def post(self):
        try:
            req_post = request.json
            new_dir = Director(**req_post)
            db.session.add(new_dir)
            db.session.commit()
            return directors_schema.dump(new_dir), 200
        except Exception:
            return 404

@directors_ns.route('/<int:id>')
class DirectorView(Resource):
    def get(self, id):
        try:
            dir = Director.query.get(id)
            if not dir:
                return '', 404
            return director_schema.dump(dir), 200
        except Exception:
            return 404

    def put(self, id):
        try:
            dir_req = request.json
            direct = Director.query.get(id)

            direct.name = dir_req.get('name')
            db.session.add(direct)
            db.session.commit()
            return director_schema.dump(direct), 204
        except Exception:
            return 404
    def delete(self, id):
        try:
            del_dir = Director.query.get(id)
            db.session.delete(del_dir)
            db.session.commit()
            return '', 200
        except Exception:
            return 404



@genres_ns.route('/')
class GenreView(Resource):
    def get(self):
        try:
            all_genres = Genre.query.all()
            if not all_genres:
                return '', 404
            return genres_schema.dump(all_genres), 201
        except Exception:
            return 404

    def post(self):
        try:
            req_genre = request.json
            genre = Genre(**req_genre)
            db.session.add(genre)
            return genre_schema.dump(genre), 201
        except Exception:
            return 404


@genres_ns.route('/<int:id>')
class GenreView(Resource):
    def get(self, id):
        try:
            genr = Genre.query.get(id)
            if not genr:
                return '', 404
            return genre_schema.dump(genr), 200
        except Exception:
            return 404


    def put(self, id):
        try:
            req_genr = request.json
            genre = Genre.query.get(id)
            genre.name = req_genr.get('name')

            db.session.add(genre)
            db.session.commit()
            return genre_schema.dump(genre), 201
        except Exception:
            return 403

    def delete(self, id):
        try:
            gen = Genre.query.get(id)
            db.session.delete(gen)
            db.session.commit()
            return '', 200
        except Exception:
            return 404


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
