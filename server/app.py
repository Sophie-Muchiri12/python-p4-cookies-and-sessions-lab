#!/usr/bin/env python3

from flask import Flask, jsonify, session
from flask_migrate import Migrate
from sqlalchemy.orm import Session
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles/<int:id>', endpoint="show_article")
def show_article(id):
    try:
        # Ensure session['page_views'] is correctly initialized
        if 'page_views' not in session:
            session['page_views'] = 0
        
        # Increment page views
        session['page_views'] += 1

        # Check if the user has exceeded the page view limit
        if session['page_views'] > 3:
            return {'message': 'Maximum pageview limit reached'}, 401

        # Fetch the article using the new SQLAlchemy 2.0 method
        article = Article.query.get(id)
        
        if article:
            # Calculate reading time
            word_count = len(article.content.split())
            minutes_to_read = max(1, round(word_count / 200))
            
            # Return the article details
            return jsonify({
                'id': article.id,
                'title': article.title,
                'content': article.content,
                'preview': article.preview,
                'author': article.user.name if article.user else "Unknown",
                'minutes_to_read': minutes_to_read,
                'date': article.date.strftime('%Y-%m-%d') if article.date else "No Date"
            }), 200
        else:
            return {'message': 'Article not found'}, 404

    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")
        return {'message': 'Internal Server Error'}, 500

if __name__ == '__main__':
    app.run(port=5555)
