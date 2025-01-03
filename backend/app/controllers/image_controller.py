from flask import request, jsonify
from app.services.image_service import process_image
from app.models.image_model import ImageModel

def remove_background():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    input_image = file.read()

    try:
        # Process the image
        processed_data = process_image(input_image)

        # Save to MongoDB
        ImageModel.insert_image({
            "original_image": input_image.decode("utf-8"),
            "foreground_image": processed_data["foreground_image"],
            "background_image": processed_data["background_image"]
        })

        return jsonify(processed_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_all_images():
    try:
        images = ImageModel.get_all_images()
        return jsonify({"images": images}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
