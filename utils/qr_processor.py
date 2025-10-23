import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import io

def extract_qr_from_image(image_file):
    """
    Extract QR code data from uploaded image file.

    Args:
        image_file: Flask file object from request.files

    Returns:
        str: QR code data if found, None otherwise
    """
    try:
        # Read image file
        image_data = image_file.read()

        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_data))

        # Convert PIL to OpenCV format
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Decode QR codes
        decoded_objects = decode(opencv_image)

        # Return first QR code data found
        for obj in decoded_objects:
            if obj.type == 'QRCODE':
                return obj.data.decode('utf-8')

        return None

    except Exception as e:
        print(f"Error processing image: {e}")
        return None