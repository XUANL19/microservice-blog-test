from flask import Flask, Response, request
from datetime import datetime
import json
from database_operations import DatabaseOperations
from flask_cors import CORS
import sys

# Create the Flask application object.
app = Flask(__name__)

CORS(app)


@app.route("/createPost", methods=["POST", "GET"])
def post_blog():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        new_blog = request.json

        owner_id = new_blog['username']
        title = new_blog["title"]
        description = new_blog["description"]
        tags = new_blog["tag"].split(" ")
        while("" in tags):
            tags.remove("")
        post_time = datetime.now().isoformat(sep=" ", timespec="seconds")

        return DatabaseOperations.new_blog_post(owner_id, title, description, post_time, tags)

    else: 
        failure_message = {'status': 'fail', 'message': 'Log in required'}
        fail_response = Response(json.dumps(failure_message), status=200, content_type="application.json")
        return fail_response
   

@app.route("/<owner_id>/myposts", methods=["POST", "GET"])
def get_blog(owner_id):
    result = DatabaseOperations.get_own_post(owner_id)
    if result:
        response = Response(json.dumps(result, default=str), status=200, content_type="application/json")
    else:
        response = Response("404 NOT FOUND", status=404, content_type="application/json")
    return response


@app.route("/allposts", methods=["GET"])
def get_all_blogs():
    result = DatabaseOperations.get_all_posts()
    if result:
        response = Response(json.dumps(result, default=str), status=200, content_type="application/json")
    else:
        response = Response("404 NOT FOUND", status=404, content_type="application/json")
    return response


@app.route("/posts/<blog_id>", methods=["GET"])
def get_blog_by_id(blog_id):
    result = DatabaseOperations.get_blog_by_blogid(blog_id)
    if result:
        response = Response(json.dumps(result, default=str), status=200, content_type="application/json")
    else:
        response = Response("404 NOT FOUND", status=404, content_type="application/json")
    return response


@app.route("/posts/<blog_id>/likecount", methods=["GET"])
def get_like_count(blog_id):
    result = DatabaseOperations.get_like_and_dislike_num(blog_id)
    result['likestate'] = 0
    if result:
        response = Response(json.dumps(result, default=str), status=200, content_type="application/json")
    else:
        response = Response("404 NOT FOUND", status=404, content_type="application/json")

    return response


@app.route("/<user_id>/posts/<blog_id>/likestate", methods=["GET"])
def get_like_state(user_id, blog_id):
    result = DatabaseOperations.like_and_dislike_state_check(user_id, blog_id)
    if result:
        response = Response(json.dumps(result, default=str), status=200, content_type="application/json")
    else:
        response = Response("404 NOT FOUND", status=404, content_type="application/json")

    return response

@app.route("/<user_id>/posts/<blog_id>/addlike", methods=["GET"])
def add_like(user_id, blog_id):
    response = DatabaseOperations.add_to_like(user_id, blog_id)
    return response


@app.route("/<user_id>/posts/<blog_id>/adddislike", methods=["GET"])
def add_dislike(user_id, blog_id):
    response = DatabaseOperations.add_to_dislike(user_id, blog_id)
    return response


@app.route("/<user_id>/posts/<blog_id>/removelike", methods=["GET"])
def remove_like(user_id, blog_id):
    response = DatabaseOperations.remove_from_like(user_id, blog_id)
    return response 


@app.route("/<user_id>/posts/<blog_id>/removedislike", methods=["GET"])
def remove_dislike(user_id, blog_id):
    response = DatabaseOperations.remove_from_dislike(user_id, blog_id)
    return response 


@app.route("/blognumber", methods=["GET"])
def get_blog_number_by_username():
    username = request.args.get('username')
    blog_num = str(DatabaseOperations.get_blog_number(username))
    response = Response(blog_num, status=200, content_type="application/json")
    return response


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5012)
    