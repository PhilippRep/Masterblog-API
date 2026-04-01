from flask import Flask, jsonify, request
from flask_cors import CORS
from operator import itemgetter
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        new_post = request.get_json()
        required_field = ["title", "content"]
        if not new_post:
            return jsonify({"error": "Invalid JSON"}), 400
        for field in required_field:
            if field not in new_post or not new_post[field].strip():
                return jsonify({"error": f"Field: {field} is required"}), 400
        new_id = max((post['id'] for post in POSTS), default=0) + 1
        new_post['id'] = new_id
        post = {
            "id": new_id,
            "title": new_post["title"],
            "content": new_post["content"]
        }
        POSTS.append(post)
        return jsonify(post), 201
    else:
        sort_posts = request.args.get('sort')
        which_direction = request.args.get('direction')
        if not sort_posts:
            return jsonify(POSTS)
        if sort_posts not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field"}), 400
        reverse = False
        if which_direction:
            if which_direction == 'desc':
                reverse= True
            elif which_direction != 'asc':
                return jsonify({"error": "Invalid sort direction"}), 400
        sorted_list = sorted(POSTS, key=itemgetter(sort_posts), reverse=reverse)
        return jsonify(sorted_list)



@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    for post in POSTS:
        if post['id'] == id:
            POSTS.remove(post)
            return jsonify({"message": f"The post with ID: {id} is deleted!"}), 200
    return jsonify({
        "error": f"No post with ID {id} found"}), 404

@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    found_post = next((post for post in POSTS if post['id'] == id), None)
    if not found_post:
        return jsonify({"error": f"No post with ID {id} found"}), 404
    new_content = request.get_json()
    if not new_content:
        return jsonify({"error": "Invalid JSON"}), 400
    if "title" in new_content and new_content["title"].strip():
        found_post["title"] = new_content["title"]
    if "content" in new_content and new_content["content"].strip():
        found_post["content"] = new_content["content"]
    return jsonify(found_post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    post_list = []
    title = request.args.get('title')
    content = request.args.get('content')
    for post in POSTS:
        if title and title.lower() in post['title'].lower():
            post_list.append(post)
        elif content and content.lower() in post['content'].lower():
            post_list.append(post)
    return jsonify(post_list), 200

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({error: "Not found"}), 404

@app.errorhandler(415)
def not_found_error(error):
    return jsonify({error: "Unsupported Media Type"}), 415

@app.errorhandler(400)
def not_found_error(error):
    return jsonify({error: "Bad Request"}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
