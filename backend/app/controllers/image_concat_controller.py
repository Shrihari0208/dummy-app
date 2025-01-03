from flask import request, jsonify
from PIL import Image
from io import BytesIO
import base64
from app.models.image_model import ImageModel

def concatenate_images():
    try:
        if 'image1' not in request.files or 'image2' not in request.files:
            return {"error": "Two images must be provided"}, 400

        orientation = request.form.get('orientation', 'horizontal')  # Default is horizontal
        image1 = Image.open(request.files['image1']).convert("RGBA")
        image2 = Image.open(request.files['image2']).convert("RGBA")

        if orientation == 'horizontal':
            combined_width = image1.width + image2.width
            combined_height = max(image1.height, image2.height)
            combined_image = Image.new("RGBA", (combined_width, combined_height))
            combined_image.paste(image1, (0, 0))
            combined_image.paste(image2, (image1.width, 0))
        elif orientation == 'vertical':
            combined_width = max(image1.width, image2.width)
            combined_height = image1.height + image2.height
            combined_image = Image.new("RGBA", (combined_width, combined_height))
            combined_image.paste(image1, (0, 0))
            combined_image.paste(image2, (0, image1.height))
        else:
            return {"error": "Invalid orientation. Use 'horizontal' or 'vertical'."}, 400

        # Convert combined image to Base64
        buffer = BytesIO()
        combined_image.save(buffer, format="PNG")
        combined_image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Save to MongoDB
        ImageModel.insert_image({
            "combined_image": combined_image_base64
        })

        return jsonify({
            "combined_image": combined_image_base64
        })

    except Exception as e:
        return {"error": str(e)}, 500
