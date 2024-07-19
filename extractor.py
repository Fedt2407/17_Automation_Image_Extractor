# Description: Extract images from a PDF file and save them as JPEG images.

import fitz  # PyMuPDF
import os
from PIL import Image
from io import BytesIO

def save_images_from_pdf(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Loop through each page
    for page_number in range(len(pdf_document)):
        # Create a folder for each page
        page_folder = os.path.join(output_folder, f"page_{page_number + 1}")
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)
        
        # Get the page
        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)
        
        # Loop through each image
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Convert image bytes to PIL Image and save as JPEG
            image = Image.open(BytesIO(image_bytes))
            image_path = os.path.join(page_folder, f"image_{img_index}.jpeg")
            image.save(image_path, "JPEG")
            
            print(f"Saved {image_path}")

# Path to your PDF file
pdf_path = './pdf_file/PS25.pdf'

# Get the base name of the PDF file (e.g., "PS25.pdf")
pdf_base_name = os.path.basename(pdf_path)

# Remove the file extension (e.g., "PS25")
pdf_name_without_extension = os.path.splitext(pdf_base_name)[0]

# Output folder to save the images, now using the modified name
output_folder = f'./{pdf_name_without_extension}_images'

save_images_from_pdf(pdf_path, output_folder)