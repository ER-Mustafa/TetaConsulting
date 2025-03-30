from PIL import Image
import pytesseract

# Install tesseract first: https://github.com/UB-Mannheim/tesseract/wiki
# pip install pytesseract pillow

def extract_text_from_image(image_path):
    # Open the image file
    img = Image.open(image_path)
    
    # Extract text using Tesseract
    text = pytesseract.image_to_string(img, lang='tur')  # 'tur' for Turkish
    
    return text

# Usage
extracted_text = extract_text_from_image('efatura.webp')
print(extracted_text)