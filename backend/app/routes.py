from app.controllers.auth_controller import register, login, check_user
from app.controllers.image_controller import remove_background, get_all_images
from app.controllers.image_concat_controller import concatenate_images

def init_routes(app):
    # Auth routes
    app.add_url_rule('/register', 'register', register, methods=['POST'])
    app.add_url_rule('/login', 'login', login, methods=['POST'])
    app.add_url_rule('/check_user', 'check_user', check_user, methods=['GET'])

    # Image routes
    app.add_url_rule('/remove-background', 'remove_background', remove_background, methods=['POST'])
    app.add_url_rule('/images', 'get_all_images', get_all_images, methods=['GET'])



    # Concatenate API
    app.add_url_rule('/concatenate-images', 'concatenate_images', concatenate_images, methods=['POST'])
