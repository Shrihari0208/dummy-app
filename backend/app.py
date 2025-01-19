from flask import Flask, request, jsonify
from flask_cors import CORS

from rembg import remove
from PIL import Image, ImageDraw, ImageFont, ImageChops

from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import io
import base64

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
    font_size = int(request.form.get('font_size', 40))
    text_color = request.form.get('text_color', "#000000")
    x_position = int(request.form.get('x_position', 50))
    y_position = int(request.form.get('y_position', 50))

    try:
        # Load the image using OpenCV
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
        if cv_image is None:
            return jsonify({'error': 'Invalid image'}), 400

        # Load a pre-trained MobileNet-SSD model
        net = cv2.dnn.readNetFromCaffe(
            'deploy.prototxt',  # Path to the prototxt file
            'mobilenet_iter_73000.caffemodel'  # Path to the pre-trained model
        )

        # Prepare the image for detection
        h, w = cv_image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv_image, scalefactor=0.007843, size=(300, 300), mean=(127.5, 127.5, 127.5), swapRB=True)
        net.setInput(blob)

        # Perform detection
        detections = net.forward()

        # Assume the largest detected object is the main subject
        subject_box = None
        max_confidence = 0
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                if confidence > max_confidence:
                    max_confidence = confidence
                    subject_box = (startX, startY, endX, endY)

        if subject_box is None:
            return jsonify({'error': 'No subject detected'}), 400

        # Separate the subject and background
        (startX, startY, endX, endY) = subject_box
        subject = cv_image[startY:endY, startX:endX]
        mask = np.zeros(cv_image.shape[:2], dtype="uint8")
        cv2.rectangle(mask, (startX, startY), (endX, endY), 255, -1)

        # Convert the image to RGBA for Pillow
        image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGBA))

        # Create a text layer
        text_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_layer)

        # Load the font
        try:
            font = ImageFont.truetype("arial.ttf", size=font_size)
        except Exception:
            font = ImageFont.load_default()

        # Calculate text position
        text_bbox = draw.textbbox((0, 0), user_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_position = (
            int(image.size[0] * x_position / 100 - text_width / 2),
            int(image.size[1] * y_position / 100 - text_height / 2),
        )

        # Draw text on the text layer
        draw.text(text_position, user_text, fill=text_color, font=font)

        # Composite the text layer behind the subject
        subject_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        subject_layer.paste(Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGBA)), mask=Image.fromarray(mask))
        final_image = Image.alpha_composite(subject_layer, text_layer)

        # Convert final image to base64
        final_buffer = io.BytesIO()
        final_image.save(final_buffer, format="PNG")
        final_base64 = base64.b64encode(final_buffer.getvalue()).decode('utf-8')

        return jsonify({'final_image': final_base64}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to process the image. Error: {str(e)}'}), 500


# advance
@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Image file and text are required'}), 400

    image_file = request.files['image']
    user_text = request.form['text']
    font_size = int(request.form.get('font_size', 40))
    text_color = request.form.get('text_color', "#000000")
    x_position = int(request.form.get('x_position', 50))
    y_position = int(request.form.get('y_position', 50))

    try:
        # Load the image
        input_image = Image.open(image_file).convert("RGBA")

        # Remove the background
        output_image = remove(input_image).convert("RGBA")

        # Create a new background layer (e.g., white)
        background = Image.new("RGBA", input_image.size, (255, 255, 255, 255))

        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", size=font_size)
        except IOError:
            font = ImageFont.load_default()

        # Initialize drawing context
        draw = ImageDraw.Draw(background)

        # Calculate text bounding box
        text_bbox = draw.textbbox((0, 0), user_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate text position
        text_x = int((input_image.width - text_width) * x_position / 100)
        text_y = int((input_image.height - text_height) * y_position / 100)

        # Add text to the background
        draw.text((text_x, text_y), user_text, font=font, fill=text_color)

        # Ensure both images are the same size
        if background.size != output_image.size:
            output_image = output_image.resize(background.size)

        # Composite the subject image over the background
        final_image = Image.alpha_composite(background, output_image)

        # Save to a bytes buffer
        buffered = io.BytesIO()
        final_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({'image': img_str}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
