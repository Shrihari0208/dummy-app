from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from rembg import remove
from PIL import Image, ImageDraw, ImageFont, ImageChops
import io

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from your frontend

# Existing API: Remove Background
@app.route('/remove-background', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400

    image_file = request.files['image']

    try:
        # Validate and open the image
        try:
            image = Image.open(image_file).convert("RGBA")
        except Exception as e:
            return jsonify({'error': f'Invalid image file. Error: {str(e)}'}), 400

        # Remove the background to get the subject (foreground)
        try:
            foreground = remove(image)  # Subject with a transparent background
        except Exception as e:
            return jsonify({'error': f'Background removal failed. Error: {str(e)}'}), 500

        # Generate the isolated object (background only)
        try:
            mask = foreground.split()[-1]  # Alpha channel as a mask
            isolated_background = Image.composite(
                Image.new("RGBA", image.size, (255, 255, 255, 0)),  # Fully transparent background
                image,
                ImageChops.invert(mask)  # Invert the alpha mask to get the background only
            )
        except Exception as e:
            return jsonify({'error': f'Isolated object generation failed. Error: {str(e)}'}), 500

        # Generate the residual background (backdrop with the subject area transparent)
        try:
            residual_background = Image.composite(
                image,  # Original image
                Image.new("RGBA", image.size, (255, 255, 255, 0)),  # Fully transparent background
                mask  # Alpha mask to make the subject area transparent
            )
        except Exception as e:
            return jsonify({'error': f'Residual background generation failed. Error: {str(e)}'}), 500

        # Convert images to Base64
        # Foreground image
        foreground_buffer = io.BytesIO()
        foreground.save(foreground_buffer, format="PNG")
        foreground_base64 = base64.b64encode(foreground_buffer.getvalue()).decode('utf-8')

        # Isolated background (image with no subject)
        isolated_buffer = io.BytesIO()
        isolated_background.save(isolated_buffer, format="PNG")
        isolated_base64 = base64.b64encode(isolated_buffer.getvalue()).decode('utf-8')

        # Residual background (backdrop with transparent subject)
        residual_buffer = io.BytesIO()
        residual_background.save(residual_buffer, format="PNG")
        residual_base64 = base64.b64encode(residual_buffer.getvalue()).decode('utf-8')

        return jsonify({
            'foreground_image': foreground_base64,  # Subject with transparent background
            'isolated_object': isolated_base64,     # Image with no subject
            'residual_background': residual_base64  # Background with subject area transparent
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to process the image. Error: {str(e)}'}), 500


@app.route('/add-text-behind', methods=['POST'])
def add_text_behind():
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Image file and text are required'}), 400

    image_file = request.files['image']
    user_text = request.form['text']

    try:
        # Validate and open the image
        try:
            image = Image.open(image_file).convert("RGBA")
        except Exception as e:
            return jsonify({'error': f'Invalid image file. Error: {str(e)}'}), 400

        # Remove the background to get the subject (foreground)
        try:
            foreground = remove(image)  # Subject with a transparent background
            mask = foreground.split()[-1]  # Alpha channel as a mask
        except Exception as e:
            return jsonify({'error': f'Background removal failed. Error: {str(e)}'}), 500

        # Generate the text background
        try:
            text_background = Image.new("RGBA", image.size, (255, 255, 255, 255))  # White background
            draw = ImageDraw.Draw(text_background)

            # Load a font
            try:
                font = ImageFont.truetype("arial.ttf", size=40)  # Adjust size as needed
            except Exception:
                font = ImageFont.load_default()  # Use default font if TTF font is unavailable

            # Calculate text size using textbbox
            text_bbox = draw.textbbox((0, 0), user_text, font=font)  # Get text bounding box
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Center the text on the background
            text_position = ((image.size[0] - text_width) // 2, (image.size[1] - text_height) // 2)

            # Add the text to the background
            draw.text(text_position, user_text, fill="black", font=font)
        except Exception as e:
            return jsonify({'error': f'Text generation failed. Error: {str(e)}'}), 500

        # Combine text background with isolated object
        try:
            combined_image = Image.composite(foreground, text_background, mask)  # Overlay foreground on text background
        except Exception as e:
            return jsonify({'error': f'Failed to combine text and object. Error: {str(e)}'}), 500

        # Convert the final image to Base64
        final_buffer = io.BytesIO()
        combined_image.save(final_buffer, format="PNG")
        final_base64 = base64.b64encode(final_buffer.getvalue()).decode('utf-8')

        return jsonify({
            'final_image': final_base64  # Combined image with text behind the isolated object
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to process the image. Error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
