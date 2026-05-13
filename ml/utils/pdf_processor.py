import fitz  # PyMuPDF
import os
from PIL import Image
import io

def split_pdf_to_images(pdf_path: str, output_dir: str):
    """
    Splits a bulk exam PDF into individual page images.
    In a real scenario, this would also detect student ID regions.
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(output_dir, f"page_{i}.png")
        pix.save(img_path)
        image_paths.append(img_path)
        
    return image_paths

def crop_answer_region(image_path: str, box: tuple, output_path: str):
    """
    Crops a specific question region from a page image.
    box: (left, top, right, bottom)
    """
    img = Image.open(image_path)
    cropped = img.crop(box)
    cropped.save(output_path)
    return output_path
