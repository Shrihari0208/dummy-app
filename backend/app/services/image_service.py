from PIL import Image, ImageChops
from io import BytesIO
import base64
from rembg import remove

def process_image(input_image):
    # Convert input to a PIL Image for processing
    original_image = Image.open(BytesIO(input_image)).convert("RGBA")
    
    # Remove the background
    output_image_bytes = remove(input_image)
    output_image = Image.open(BytesIO(output_image_bytes)).convert("RGBA")
    
    # Create the removed background
    removed_background = ImageChops.difference(original_image, output_image)
    removed_background = ImageChops.add(
        removed_background,
        Image.new("RGBA", original_image.size, (255, 255, 255, 0))
    )

    # Convert images to Base64
    def encode_image(image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "foreground_image": encode_image(output_image),
        "background_image": encode_image(removed_background),
    }
