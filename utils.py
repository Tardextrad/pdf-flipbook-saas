import os
import uuid
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def process_pdf(pdf_path, output_dir):
    try:
        images = convert_from_path(pdf_path)
        image_files = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f'page_{i + 1}.jpg')
            image.save(image_path, 'JPEG')
            image_files.append(image_path)
        return image_files
    except Exception as e:
        raise Exception(f"Error converting PDF: {str(e)}")

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{str(uuid.uuid4())}.{ext}"
