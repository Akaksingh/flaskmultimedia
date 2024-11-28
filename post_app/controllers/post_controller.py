from flask import request,send_from_directory,jsonify
from post_app.services.post_service import PostService
from post_app.views.post_view import PostView
import os
from flask import request, current_app
from werkzeug.utils import secure_filename
from shared.utils.db_utils import db


class PostController:
    @staticmethod
    def get_all_posts():
        posts = PostService.get_all_posts()
        return PostView.render_posts(posts), 200

    @staticmethod
    def get_post(post_id):
        post = PostService.get_post_by_id(post_id)
        if not post:
            return PostView.render_error('Post not found'), 404
        return PostView.render_post(post), 200




    
    @staticmethod
    def create_post():
        
        data = request.form
        user_id = data.get('user_id')
        content = data.get('content')
        file = request.files.get('file')  
        
       
        post = PostService.create_post(user_id, content, file)
        
        return PostView.render_success('Post created successfully', post.post_id), 201
    

    
    @staticmethod
    def get_post_media(post_id):
        media_file = PostService.get_media_filename(post_id)
        
        if not media_file:
            return PostView.render_error({"Media not found"}), 404

        return send_from_directory(os.path.join(current_app.root_path, 'uploads'), media_file)
    
    @staticmethod
    def update_post(post_id):
        data = request.get_json()
        new_content = data.get('content')

        post = PostService.update_post(post_id, new_content)
        if post:
            return PostView.render_success('Post updated successfully', post.post_id), 200
        return PostView.render_error('Post not found'), 404

    @staticmethod
    def delete_post(post_id):
        post = PostService.delete_post(post_id)
        if post:
            return PostView.render_success('Post deleted successfully', post.post_id), 200
        return PostView.render_error('Post not found'), 404

    @staticmethod
    def crop_media():
        data = request.get_json()
        
        # Validate input
        post_id = data.get('post_id')
        crop_factor = data.get('crop_factor')

        if not post_id or not isinstance(post_id, int):
            return {"error": "Invalid or missing post_id"}, 400
        if not crop_factor or not isinstance(crop_factor, int):
            return {"error": "Invalid or missing crop_factor"}, 400

        # Call the service layer function
        try:
            PostService.scale_to_multiple(post_id, crop_factor)
            return {"message": f"Media for post ID {post_id} cropped to the nearest multiple of {crop_factor}"}, 200
        except FileNotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
        
    @staticmethod
    def convert_to_greyscale():
        data = request.get_json()
        post_id = data.get('post_id')

        try:
            PostService.convert_to_greyscale(post_id)
            return jsonify({"message": f"Media for post {post_id} converted to greyscale successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 400

    @staticmethod
    def adjust_brightness():
        data = request.get_json()
        post_id = data.get('post_id')
        brightness_factor = data.get('brightness_factor')  # Expected to be a float (e.g., 1.2 for 20% brighter)

        try:
            PostService.adjust_brightness(post_id, brightness_factor)
            return jsonify({"message": f"Brightness of media for post {post_id} adjusted successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 400