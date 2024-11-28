from shared.models.post_model import Post
from shared.utils.db_utils import db
from werkzeug.utils import secure_filename
from flask import send_from_directory, current_app
import os
from PIL import Image,ImageEnhance
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip

from PIL import Image
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'wav'}


def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


MAX_FILE_SIZE = 100 * 1024 * 1024  
MAX_IMAGE_WIDTH = 1920
MAX_IMAGE_HEIGHT = 1080
MAX_VIDEO_WIDTH = 1920
MAX_VIDEO_HEIGHT = 1080

def validate_and_process_file(file, filename, upload_folder):
    if file.content_length > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the allowed limit of 100MB")

    if not allowed_file(filename):
        raise ValueError("File format not allowed")

    
    file_path = os.path.join(upload_folder, filename)

    
    if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
        image = Image.open(file)
        width, height = image.size

        
        if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
            new_width = min(width, MAX_IMAGE_WIDTH)
            new_height = min(height, MAX_IMAGE_HEIGHT)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            #lanczos sinc hai bhaiiiiiiii
        
        image.save(file_path, format=image.format)
        print(f"Image saved to: {file_path}")  
        return file_path

    
    if filename.rsplit('.', 1)[1].lower() in {'mp4', 'mp3', 'wav'}:
        video = VideoFileClip(file)
        width, height = video.size

        
        if width > MAX_VIDEO_WIDTH or height > MAX_VIDEO_HEIGHT:
            new_width = min(width, MAX_VIDEO_WIDTH)
            new_height = min(height, MAX_VIDEO_HEIGHT)
            video = video.resize(newsize=(new_width, new_height))

        
        video.write_videofile(file_path)
        print(f"Video saved to: {file_path}")  
        return file_path

    
    file.save(file_path)
    print(f"File saved to: {file_path}")  
    return file_path

def get_full_file_path(post_id):
            
            def get_media_filename(post_id):
                post = Post.query.get(post_id)
                if post and post.media_url:
                    return post.media_url
                return None
        
            media_filename = get_media_filename(post_id)
            if media_filename:
                upload_folder = os.path.join(current_app.root_path, 'post_app', 'uploads')
                return os.path.join(upload_folder, media_filename)
            return None

class PostService:
    @staticmethod
    def create_post(user_id, content, file=None):
        media_url = None

        if file:
            filename = secure_filename(file.filename)

            
            upload_folder = os.path.join(current_app.root_path, 'post_app', 'uploads')

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

         
            try:
                processed_file = validate_and_process_file(file, filename, upload_folder)
                media_url = filename  
            except ValueError as e:
                raise ValueError(f"File validation error: {str(e)}")

        
        new_post = Post(user_id=user_id, content=content, media_url=media_url)
        db.session.add(new_post)
        db.session.commit()
        return new_post

    @staticmethod
    def get_post_by_id(post_id):
        return Post.query.get(post_id)

    @staticmethod
    def get_posts_by_user(user_id):
        return Post.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_all_posts():
        return Post.query.order_by(Post.created_at.desc()).all()

    @staticmethod
    def update_post(post_id, new_content):
        post = Post.query.filter_by(post_id=post_id).first()
        if post:
            post.content = new_content
            db.session.commit()
        return post

    @staticmethod
    def delete_post(post_id):
        post = Post.query.filter_by(post_id=post_id).first()
        if post:
            db.session.delete(post)
            db.session.commit()
        return post



    @staticmethod
    def get_media_filename(post_id):
        # Fetch the post using the post_id
        post = Post.query.get(post_id)

        # Return the media_url if it exists
        if post and post.media_url:
            return post.media_url
        return None
    
    @staticmethod
    def serve_media(media_url):
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        return send_from_directory(upload_folder, media_url)
    


    @staticmethod
    def scale_to_multiple(post_id, crop_factor):
        try:
            # Fetch the file path using the helper function
            file_path = get_full_file_path(post_id)
            if not file_path:
                raise FileNotFoundError("Media file not found for the given post ID.")
            
            # Open the image
            image = Image.open(file_path)
            original_width, original_height = image.size

            # Calculate the dimensions for the crop
            new_width = int(original_width / crop_factor)
            new_height = int(original_height / crop_factor)

            # Ensure dimensions are valid
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Crop factor is too large, resulting in invalid dimensions.")

            left = (original_width - new_width) // 2
            top = (original_height - new_height) // 2
            right = left + new_width
            bottom = top + new_height

            cropped_image = image.crop((left, top, right, bottom))
            cropped_image.save(file_path)  

            print(f"Image cropped with factor {crop_factor} for post {post_id}: {file_path}")

        except FileNotFoundError:
            raise  # Re-raise the exception for the controller to handle
        except Exception as e:
            raise Exception(f"Error cropping image for post {post_id}: {str(e)}")

    @staticmethod
    def convert_to_greyscale(post_id):
        try:
            file_path = get_full_file_path(post_id)
            if not file_path:
                raise FileNotFoundError("Media file not found for the given post ID.")

            image = Image.open(file_path)

            greyscale_image = image.convert("L")
            greyscale_image.save(file_path)  

            print(f"Image converted to greyscale for post {post_id}: {file_path}")

        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Error converting image to greyscale for post {post_id}: {str(e)}")

    @staticmethod
    def adjust_brightness(post_id, brightness_factor):
        try:
            file_path = get_full_file_path(post_id)
            if not file_path:
                raise FileNotFoundError("Media file not found for the given post ID.")

            image = Image.open(file_path)

            enhancer = ImageEnhance.Brightness(image)
            adjusted_image = enhancer.enhance(brightness_factor)
            adjusted_image.save(file_path)  

            print(f"Brightness adjusted with factor {brightness_factor} for post {post_id}: {file_path}")

        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Error adjusting brightness for post {post_id}: {str(e)}")
