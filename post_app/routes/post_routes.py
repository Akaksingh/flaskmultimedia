from flask import Blueprint
from post_app.controllers.post_controller import PostController
from shared.models.post_model import Post
from views.post_view import PostView 
from flask import send_from_directory, current_app
import os

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/api/posts', methods=['GET'])
def get_all_posts():
    return PostController.get_all_posts()

@post_bp.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    return PostController.get_post(post_id)

@post_bp.route('/api/posts', methods=['POST'])
def create_post():
    return PostController.create_post()

@post_bp.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    return PostController.update_post(post_id)

@post_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    return PostController.delete_post(post_id)



@post_bp.route('/api/post/media>', methods=['GET'])
def get_post_media(post_id):
    return PostController.get_post_media(post_id)

# Route to get media for a post
@post_bp.route('/uploads/media/<int:post_id>', methods=['GET'])
def serve_media(post_id):
    # Query the post by its ID
    post = Post.query.filter_by(post_id=post_id).first()

    if not post or not post.media_url:
        return PostView.render_error({"Media not found"}), 404

    # Construct the file path using the media_url stored in the database
    media_path = os.path.join(current_app.root_path, 'post_app', 'uploads', post.media_url)

    if not os.path.exists(media_path):
        return PostView.render_error({"File not found"}), 404

    # Serve the file from the uploads folder
    return send_from_directory(os.path.dirname(media_path), os.path.basename(media_path))


@post_bp.route('/api/post/media/crop', methods=["POST"])
def crop_media():
    try:
        return PostController.crop_media()
    except Exception as e:
        return {"error": str(e)}, 500

@post_bp.route('/api/post/media/greyscale', methods=["POST"])
def convert_to_greyscale():
    return PostController.convert_to_greyscale()

@post_bp.route('/api/post/media/brightness', methods=["POST"])
def adjust_brightness():
    return PostController.adjust_brightness()