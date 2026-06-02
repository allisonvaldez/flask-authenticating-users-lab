#!/usr/bin/env python3

# Import necessary components and utilities to run the app
from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Article, User, ArticlesSchema, UserSchema

# Create Flask app and configure db
app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Connect Flask-Migrate and connect db with app
migrate = Migrate(app, db)
db.init_app(app)

# Create Flask-RESTful API instance
api = Api(app)

# Create a class to resets session
class ClearSession(Resource):

    # Create a function to delete data from session
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204


# Create a class to return articles
class IndexArticle(Resource):

    # Create a function to search for articles and serialize them
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200


# Create a class to return one article with the paywall
class ShowArticle(Resource):

    # Create a function to display paywall
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema().dump(article)
            return make_response(article_json, 200)
        
        # Deploy paywall
        return {'message': 'Maximum pageview limit reached'}, 401


# Create a class to find user by username
class Login(Resource):

    # Create a function to retreive the username from JSON
    def post(self):
        username = request.get_json().get('username')

        # Search user in the database
        user = User.query.filter(User.username == username).first()
        
        # Control flow if user found
        if user:
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'error': 'User not found'}, 404


# Create a class to clear users from session
class Logout(Resource):

    # Create a function to delete data from session
    def delete(self):
        session['user_id'] = None
        return {}, 204


# Create a class to return the current user
class CheckSession(Resource):

    # Create a function to gather user
    def get(self):
        user_id = session.get('user_id')

        # Control flow for finding user
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return UserSchema().dump(user), 200

        return {}, 401


# Register all resources
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)